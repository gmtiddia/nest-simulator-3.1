# testsuite/CMakeLists.txt
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

set( TESTSUBDIRS
    selftests
    unittests
    regressiontests
    mpitests
    mpi_selftests
    musictests
    cpptests
    pytests
    )

add_subdirectory( selftests )
add_subdirectory( unittests )
add_subdirectory( regressiontests )
add_subdirectory( mpi_selftests/fail )
add_subdirectory( mpi_selftests/pass )
add_subdirectory( mpitests )
add_subdirectory( musictests )
add_subdirectory( cpptests )

install( DIRECTORY ${TESTSUBDIRS}
    DESTINATION ${CMAKE_INSTALL_DATADIR}/testsuite
    )

install( PROGRAMS do_tests.sh
    DESTINATION ${CMAKE_INSTALL_DATADIR}/testsuite
    )

install( FILES junit_xml.sh run_test.sh summarize_tests.py
    DESTINATION ${CMAKE_INSTALL_DATADIR}/testsuite
    )
