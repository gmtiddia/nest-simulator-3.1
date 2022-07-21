/*
 *  iaf_simple.cpp
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include "iaf_simple.h"

// C++ includes:
#include <limits>

// Includes from libnestutil:
#include "dict_util.h"
#include "numerics.h"

// Includes from nestkernel:
#include "event_delivery_manager_impl.h"
#include "exceptions.h"
#include "kernel_manager.h"
#include "universal_data_logger_impl.h"

// Includes from sli:
#include "dict.h"
#include "dictutils.h"
#include "doubledatum.h"
#include "integerdatum.h"

/* ----------------------------------------------------------------
 * Recordables map
 * ---------------------------------------------------------------- */

nest::RecordablesMap< nest::iaf_simple > nest::iaf_simple::recordablesMap_;

namespace nest
{
// Override the create() method with one call to RecordablesMap::insert_()
// for each quantity to be recorded.
template <>
void
RecordablesMap< iaf_simple >::create()
{
  // use standard names whereever you can for consistency!
  insert_( names::V_m, &iaf_simple::get_V_m_ );
}
}

/* ----------------------------------------------------------------
 * Default constructors defining default parameters and state
 * ---------------------------------------------------------------- */

nest::iaf_simple::Parameters_::Parameters_()
  : tau_m_( 10.0 )
  , E_L_( -70.0 ) 
  , V_reset_( -70.0 )
  , C_m_( 250.0 )
  , I_e_( 0.0 )
  , V_th_( -55.0 )                                   // mV
  , V_min_( -std::numeric_limits< double >::max() ) // mV
{
}

nest::iaf_simple::State_::State_()
  : v_( -70.0 )       // membrane potential
  , I_( 0.0 )         // input current
{
}

/* ----------------------------------------------------------------
 * Parameter and state extractions and manipulation functions
 * ---------------------------------------------------------------- */

void
nest::iaf_simple::Parameters_::get( DictionaryDatum& d ) const
{
  def< double >( d, names::I_e, I_e_ );
  def< double >( d, names::V_th, V_th_ ); // threshold value
  def< double >( d, names::V_min, V_min_ );
  def< double >( d, names::tau_m, tau_m_ );
  def< double >( d, names::E_L, E_L_ );
  def< double >( d, names::V_reset, V_reset_ );
  def< double >( d, names::C_m, C_m_ );
}

void
nest::iaf_simple::Parameters_::set( const DictionaryDatum& d, Node* node )
{

  updateValueParam< double >( d, names::V_th, V_th_, node );
  updateValueParam< double >( d, names::V_min, V_min_, node );
  updateValueParam< double >( d, names::I_e, I_e_, node );
  updateValueParam< double >( d, names::tau_m, tau_m_, node );
  updateValueParam< double >( d, names::E_L, E_L_, node );
  updateValueParam< double >( d, names::V_reset, V_reset_, node );
  updateValueParam< double >( d, names::C_m, C_m_, node );

}

void
nest::iaf_simple::State_::get( DictionaryDatum& d, const Parameters_& ) const
{
  def< double >( d, names::V_m, v_ ); // Membrane potential
}

void
nest::iaf_simple::State_::set( const DictionaryDatum& d, const Parameters_&, Node* node )
{
  updateValueParam< double >( d, names::V_m, v_, node );
}

nest::iaf_simple::Buffers_::Buffers_( iaf_simple& n )
  : logger_( n )
{
}

nest::iaf_simple::Buffers_::Buffers_( const Buffers_&, iaf_simple& n )
  : logger_( n )
{
}

/* ----------------------------------------------------------------
 * Default and copy constructor for node
 * ---------------------------------------------------------------- */

nest::iaf_simple::iaf_simple()
  : ArchivingNode()
  , P_()
  , S_()
  , B_( *this )
{
  recordablesMap_.create();
}

nest::iaf_simple::iaf_simple( const iaf_simple& n )
  : ArchivingNode( n )
  , P_( n.P_ )
  , S_( n.S_ )
  , B_( n.B_, *this )
{
}

/* ----------------------------------------------------------------
 * Node initialization functions
 * ---------------------------------------------------------------- */

void
nest::iaf_simple::init_buffers_()
{
  B_.spikes_.clear();   // includes resize
  B_.currents_.clear(); // includes resize
  B_.logger_.reset();   // includes resize
  ArchivingNode::clear_history();
}

void
nest::iaf_simple::calibrate()
{
  B_.logger_.init();
}

/* ----------------------------------------------------------------
 * Update and spike handling functions
 */

void
nest::iaf_simple::update( Time const& origin, const long from, const long to )
{
  assert( to >= 0 && ( delay ) from < kernel().connection_manager.get_min_delay() );
  assert( from < to );

  const double h = Time::get_resolution().get_ms();

  for ( long lag = from; lag < to; ++lag )
  {
    // neuron is never refractory
    // use standard forward Euler numerics
    // set input current

    double P22 = std::exp( -h / P_.tau_m_ );
    double P20 = P_.tau_m_ / P_.C_m_ * ( 1.0 - P22 );

    
    S_.I_ = B_.currents_.get_value( lag );
    double I_syn = B_.spikes_.get_value( lag );
    //printf("S_.v_: %lf\th: %lf\tP_.I_e_: %lf\n", S_.v_, h,  P_.I_e_);
    //S_.v_ += h * P_.I_e_ / P_.C_m_ + S_.I_ + I_syn;
    S_.v_ += P_.I_e_ * P20 + S_.I_ + I_syn;
    //printf("S_.v_: %lf\th: %lf\tP_.I_e_: %lf\n", S_.v_, h,  P_.I_e_);

    // threshold crossing
    if ( S_.v_ >= P_.V_th_ )
    {
      S_.v_ = P_.V_reset_;

      // compute spike time
      set_spiketime( Time::step( origin.get_steps() + lag + 1 ) );

      SpikeEvent se;
      kernel().event_delivery_manager.send( *this, se, lag );
    }
    //printf("S_.v_: %lf\th: %lf\tP_.tau_m_: %lf\n", S_.v_, h,  P_.tau_m_);
    S_.v_ = ( S_.v_ - P_.E_L_ ) * std::exp( - h / P_.tau_m_ ) + P_.E_L_;
    //printf("S_.v_: %lf\th: %lf\tP_.tau_m_: %lf\n", S_.v_, h,  P_.tau_m_);
    // lower bound of membrane potential
    S_.v_ = ( S_.v_ < P_.V_min_ ? P_.V_min_ : S_.v_ );

    // voltage logging
    B_.logger_.record_data( origin.get_steps() + lag );
  }
}

void
nest::iaf_simple::handle( SpikeEvent& e )
{
  assert( e.get_delay_steps() > 0 );
  B_.spikes_.add_value(
    e.get_rel_delivery_steps( kernel().simulation_manager.get_slice_origin() ), e.get_weight() * e.get_multiplicity() );
}

void
nest::iaf_simple::handle( CurrentEvent& e )
{
  assert( e.get_delay_steps() > 0 );

  const double c = e.get_current();
  const double w = e.get_weight();
  B_.currents_.add_value( e.get_rel_delivery_steps( kernel().simulation_manager.get_slice_origin() ), w * c );
}

void
nest::iaf_simple::handle( DataLoggingRequest& e )
{
  B_.logger_.handle( e );
}
