# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:42:53 2014

@author: jpeacock-pr
"""

import mtpy.modeling.modem_new as modem
import mtpy.modeling.ws3dinv as ws
import scipy.interpolate as spi
import numpy as np
import time

ws_model_fn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\Coarse2Fine_Inv2\mb_model.09"
ws_data_fn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\Coarse2Fine_Inv2\WSDataFile.dat"

model_fn = r"c:\MinGW32-xy\Peacock\ModEM\WS_StartingModel_03b\Modular_NLCG_012.rho"
data_fn = r"c:\MinGW32-xy\Peacock\ModEM\WS_StartingModel_03b\mb_data.dat"

md = modem.Data()
md.read_data_file(data_fn)

mod_model = modem.Model()
mod_model.read_model_file(model_fn)

new_mod_model = modem.Model()

wsd = ws.WSData()
wsd.read_data_file(ws_data_fn)

wsm = ws.WSModel()
wsm.model_fn = ws_model_fn
wsm.read_model_file()

new_mod_model.station_locations = md.coord_array.copy()
new_mod_model.cell_size_east = 500
new_mod_model.cell_size_north = 500
new_mod_model.n_layers = 43
new_mod_model.z1_layer = 10
new_mod_model.pad_east = 12
new_mod_model.pad_north = 12
new_mod_model.pad_stretch_h = 1.5
new_mod_model.z_bottom = 200000
new_mod_model.z_target_depth = 40000
new_mod_model.make_mesh()


print 'Start Time = {0}'.format(time.ctime())
#------- Interpolate onto a new mesh ------------
#1) first need to make x, y, z have dimensions (nx, ny, nz), similar to res
north, east, vert = np.broadcast_arrays(wsm.grid_north[:, None, None], 
                                        wsm.grid_east[None, :, None], 
                                        wsm.grid_z[None, None, :])

#2) next interpolate ont the new mesh
new_res = spi.griddata((north.ravel(), east.ravel(), vert.ravel()),
                        wsm.res_model.ravel(),
                        (new_mod_model.grid_north[:, None, None], 
                         new_mod_model.grid_east[None, :, None], 
                         new_mod_model.grid_z[None, None, :]),
                         method='linear')

new_mod_model.res_model = new_res

new_mfn = r"c:\MinGW32-xy\Peacock\ModEM\WS_StartingModel_03b\mb_remesh.ws"
new_mod_model.write_model_file(model_fn=new_mfn)

print 'End Time = {0}'.format(time.ctime())



