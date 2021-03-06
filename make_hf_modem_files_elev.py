# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:02:57 2015

Add topography to ModEM models and data file, and covariance

@author: jpeacock
"""
#==============================================================================
# Imports
#==============================================================================
import os
import mtpy.modeling.modem as modem

#==============================================================================
# Input files
#==============================================================================
dem_fn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\dem\umatilla_dem_200m.txt"

data_fn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\modem_inv\inv01\hf_modem_data_err03.dat"
model_fn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\modem_inv\inv01\hf_sm02.rho"

# path to save files to
sv_path = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\modem_inv\inv01"

if not os.path.exists(sv_path):
    os.mkdir(sv_path)
#==============================================================================
# Input Parameters
#==============================================================================
# number of cells to make elevation similar from edge of model
pad = 5

# cell size of dem
dem_cell_size = 200.

# air resistivity
res_air = 1e12

# size of elevation cells
elev_cell = 20

##==============================================================================
##  Do all the work
##==============================================================================
m_obj = modem.Model()
m_obj.read_model_file(model_fn)

d_obj = modem.Data()
d_obj.read_data_file(data_fn)

# sometimes you need to adjust the center of the model, distance is in meters
model_center = (d_obj.center_point.east-0.00, 
                     d_obj.center_point.north+0.00)

# add topography to model, can set a max elevation to remove isolated peaks
# which can cause errors in ModEM
new_model_fn = m_obj.add_topography_to_model(dem_fn,
                                             write_file=True,
                                             model_center=model_center,
                                             cell_size=dem_cell_size, 
                                             elev_cell=elev_cell,
                                             elev_max=800.,
                                             dem_rotation_angle=0)
                                              

#write new data file
d_obj.center_stations(new_model_fn) 
d_obj.change_data_elevation(new_model_fn)

n_dfn = d_obj.write_data_file(save_path=sv_path, 
                              fn_basename='hf_data_ef03_tec.dat',
                              fill=False, 
                              compute_error=False,
                              elevation=True)

# write covariance file
cov = modem.Covariance()
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.save_path = sv_path
cov.write_covariance_file(model_fn=new_model_fn)

# make paraview files if needed
m_obj.write_vtk_file()
d_obj.write_vtk_station_file()

# plot the model and make sure everything looks good
mm = modem.ModelManipulator(model_fn=new_model_fn, 
                            data_fn=n_dfn, 
                            depth_index=27)