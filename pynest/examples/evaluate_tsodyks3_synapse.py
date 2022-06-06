# -*- coding: utf-8 -*-
#
# evaluate_tsodyks3_synapse.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.


"""
Example of the tsodyks3_synapse in NEST
---------------------------------------

This synapse model implements synaptic short-term depression and short-term
facilitation according to [1]_. It solves Eq (5) and Eq (6) from 
Supporting material of [1]_.

This connection merely scales the synaptic weight, based on the spike history
and the parameters of the kinetic model. Thus, it is suitable for all types
of synaptic dynamics, that is current or conductance based.

The quantity ux in the synapse properties is the
factor that scales the synaptic weight.

.. warning::

   This synaptic plasticity rule does not take
   :doc:`precise spike timing <simulations_with_precise_spike_times>` into
   account. When calculating the weight update, the precise spike time part
   of the timestamp is ignored.

Parameters
++++++++++

The following parameters can be set in the status dictionary:

* U             - Increase in u with each spike [0,1], default=0.5
* u             - The probability of release (U_se) [0,1], default=0.5
* x             - Amount of available resources [0,1], default=1.0
* tau_fac  ms   - Time constant for facilitation, default = 0(off)
* tau_rec  ms   - Time constant for depression, default = 800ms


Notes
~~~~~

This example is based on the NEST example evaluate_tsodyks2_synapse.
Here, an additional postsynaptic neuron is simulated and connected
to the presynaptic neuron using the tsodyks3_synapse model.
Under identical conditions, the tsodyks3_synapse produces
slightly higher peak amplitudes than the tsodyks_synapse. However,
the qualitative behavior is identical.

References
~~~~~~~~~~

.. [1] Mongillo G, Barak O, Tsodyks M (2008). Synaptic Theory of Working
       Memory. Science 319, 1543–1546.
       DOI: https://doi.org/10.1126/science.1150769

"""

import nest
import nest.voltage_trace
import numpy as np
import matplotlib.pyplot as plt

nest.ResetKernel()

###############################################################################
# Parameter set for depression

dep_params = {"U": 0.67, "u": 0.67, 'x': 1.0, "tau_rec": 450.0,
              "tau_fac": 0.0, "weight": 250.}

###############################################################################
# Parameter set for facilitation

fac_params = {"U": 0.2, "u": 0.2, 'x': 1.0, 'y': 0.0, "tau_fac": 1500.,
              "tau_rec": 200., "weight": 100.}
fac_params2 = {"U": 0.2, "u": 0.2, 'x': 1.0, "tau_fac": 1500.,
              "tau_rec": 200., "weight": 100.}
fac_params3 = {"U": 0.2, "u": 0.2, 'x': 1.0, "tau_fac": 1500.,
              "tau_rec": 200., "weight": 100.}

###############################################################################
# Now we assign the parameter set to the synapse models.

tsodyks_params = dict(fac_params, synapse_model="tsodyks_synapse")     # for tsodyks_synapse
tsodyks2_params = dict(fac_params2, synapse_model="tsodyks2_synapse")  # for tsodyks2_synapse
tsodyks3_params = dict(fac_params3, synapse_model="tsodyks3_synapse")  # for tsodyks3_synapse

###############################################################################
# Create four neurons.

neuron = nest.Create("iaf_psc_exp", 4, params={"tau_syn_ex": 2.})

###############################################################################
# Neuron one produces spikes. Neurons 2, 3 and 4 receive the spikes via the
# synapse models.

nest.Connect(neuron[0], neuron[1], syn_spec=tsodyks_params)
nest.Connect(neuron[0], neuron[2], syn_spec=tsodyks2_params)
nest.Connect(neuron[0], neuron[3], syn_spec=tsodyks3_params)

###############################################################################
# Now create the voltmeters to record the responses.

voltmeter = nest.Create("voltmeter", 3, params={'interval': 0.1})

###############################################################################
# Connect the voltmeters to the neurons.

nest.Connect(voltmeter[0], neuron[1])
nest.Connect(voltmeter[1], neuron[2])
nest.Connect(voltmeter[2], neuron[3])

###############################################################################
# Now simulate the standard STP protocol: a burst of spikes, followed by a
# pause and a recovery response.

sim1 = 500.0
sim2 = 1000.0
sim3 = 500.0


neuron[0].I_e = 376.0
nest.Simulate(sim1)

neuron[0].I_e = 0.0
nest.Simulate(sim2)

neuron[0].I_e = 376.0
nest.Simulate(sim3)


###############################################################################
# Finally, generate voltage traces. Both are shown in the same plot and
# should be almost completely overlapping.


nest.voltage_trace.from_device(voltmeter[0])
nest.voltage_trace.from_device(voltmeter[1])
nest.voltage_trace.from_device(voltmeter[2])
plt.show()
