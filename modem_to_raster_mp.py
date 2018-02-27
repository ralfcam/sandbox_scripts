# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r
import os

#model_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_rot_tip02_cov03_NLCG_083.rho"
#model_fn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_02\mp_rr10_cov03_NLCG_106.rho"
model_fn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_03\mp_sm02_pr142_err05_cov02_NLCG_119.rho"
save_path = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_03\depth_slices"

#model_center = (-115.503979, 35.481154)
model_center = (-115.494148, 35.488658)
 

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print 'Made directory {0}'.format(directory_path)
        
check_dir(save_path)

modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
ll_cc = modem_raster.get_model_lower_left_coord(model_center=model_center,
                                                pad_east=7, pad_north=7)
modem_raster.lower_left_corner = (ll_cc[0]+.026, ll_cc[1]+.099)
modem_raster.save_path = save_path
modem_raster.projection = 'WGS84'
modem_raster.rotation_angle = 0.0
modem_raster.write_raster_files()