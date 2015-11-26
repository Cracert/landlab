"""Test the SedDepEroder component.

Test the sed dep eroder by turning it over a few times. No attempt has been
made to ensure the solution is stable. Takes a topo already output and runs it
a few more times, to ensure repeatability.
"""
import os

import numpy as np
from numpy.testing import assert_array_almost_equal

from landlab import RasterModelGrid
from landlab.components.flow_routing.route_flow_dn import FlowRouter
from landlab.components.stream_power.sed_flux_dep_incision import SedDepEroder
from landlab import ModelParameterDictionary


_THIS_DIR = os.path.abspath(os.path.dirname(__file__))


def test_sed_dep():
    input_file = os.path.join(_THIS_DIR, 'sed_dep_params.txt')
    inputs = ModelParameterDictionary(input_file)
    nrows = inputs.read_int('nrows')
    ncols = inputs.read_int('ncols')
    dx = inputs.read_float('dx')
    leftmost_elev = inputs.read_float('leftmost_elevation')
    initial_slope = inputs.read_float('initial_slope')
    uplift_rate = inputs.read_float('uplift_rate')

    runtime = inputs.read_float('total_time')
    dt = inputs.read_float('dt')

    nt = int(runtime//dt)
    uplift_per_step = uplift_rate * dt

    mg = RasterModelGrid((nrows, ncols), (dx, dx))

    mg.create_node_array_zeros('topographic__elevation')
    z = np.loadtxt(os.path.join(_THIS_DIR, 'seddepinit.gz'))
    mg['node']['topographic__elevation'] = z

    mg.set_closed_boundaries_at_grid_edges(False, True, False, True)

    fr = FlowRouter(mg)
    sde = SedDepEroder(mg, input_file)

    for i in xrange(nt):
        mg.at_node['topographic__elevation'][mg.core_nodes] += uplift_per_step
        mg = fr.route_flow()
        mg, _ = sde.erode(mg, dt)

    z_tg = np.loadtxt(os.path.join(_THIS_DIR, 'seddepz_tg.gz'))

    assert_array_almost_equal(mg.at_node['topographic__elevation'][
        mg.core_nodes], z_tg[mg.core_nodes])
