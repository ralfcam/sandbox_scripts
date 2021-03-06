# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""


import os
import numpy as np
import mtpy.modeling.modem as modem

#==============================================================================
# Inputs
#==============================================================================
#edi_path = r"c:\Users\jpeacock\Documents\iMush\imush_edi_files_final"
#save_path = r"c:\Users\jpeacock\Documents\iMush\modem_inv"

edi_path = r"c:\Users\jrpeacock\Google Drive\FieldWork\imush\imush_edi_files_final"
save_path = r"c:\Users\jrpeacock\Google Drive\FieldWork\imush\modem_inv"

s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]

# remove stations that are too close together.
del_list = [os.path.join(edi_path, 'mshn{0}.edi'.format(ss)) for ss in 
            [42, 46, 55, 65, 74, 76, 84, 92]]

for sd in del_list:
    s_edi_list.remove(sd)
                  
if not os.path.exists(save_path):
    os.mkdir(save_path)

#==============================================================================
# First make the mesh
#==============================================================================
#mod_obj = modem.Model(edi_list=s_edi_list)
#mod_obj.cell_size_east = 1000
#mod_obj.cell_size_north = 1000
#mod_obj.pad_east = 18
#mod_obj.pad_north = 18
#mod_obj.pad_stretch_h = 1.5
#mod_obj.pad_stretch_v = 1.5
#mod_obj.pad_z = 5
#mod_obj.n_layers = 50
#mod_obj.z1_layer = 30
#mod_obj.z_target_depth = 60000.
#
##--> here is where you can rotate the mesh
#mod_obj.mesh_rotation_angle = 0
#
#mod_obj.make_mesh()
#mod_obj.plot_mesh()
#
#mod_obj.write_model_file(model_fn=os.path.join(save_path, r"imush_modem_sm_02.rho"))

#==============================================================================
# Make the data file
#==============================================================================
inv_period_list = np.logspace(-np.log10(300), np.log10(10000), num=23)
data_obj = modem.Data(edi_list=s_edi_list,
                      period_list=inv_period_list)
data_obj.error_type_z = 'egbert_floor'
data_obj.error_value_z = 7.0
data_obj.error_value_tipper = .04
data_obj.error_type_tipper = 'abs_floor'
data_obj.inv_mode = '2'

##--> here is where you can rotate the data
data_obj.write_data_file(save_path=save_path, 
                         fn_basename="imush_modem_data_err{0:02.0f}.dat".format(data_obj.error_value_z))

#--> here is where you can rotate the data
#data_obj.write_data_file(save_path=save_path, 
#                         fn_basename="imush_modem_data_tip{0:02.0f}.dat".format(data_obj.error_value_tipper*100))

#==============================================================================
# make the covariance file
#==============================================================================
#cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
#cov.smoothing_east = 0.5
#cov.smoothing_north = 0.5
#cov.smoothing_z = 0.5
#cov.smoothing_num = 2
#
#cov.write_covariance_file(os.path.join(save_path, 'covariance.cov'))


