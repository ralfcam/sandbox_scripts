# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r
import os

#model_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_rot_tip02_cov03_NLCG_083.rho"
model_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_rot_err03_tip02_cov03_NLCG_016.rho"


save_path = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_final_mt_model_slices"
#save_path = r"/mnt/hgfs/jpeacock/Documents/LV/Maps/geo_model_slices_02"
#model_center = (-118.833, 37.815) # lv center
model_center = (-121.686989, 48.723422 )

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print 'Made directory {0}'.format(directory_path)
        
check_dir(save_path)

#ll_cc = (-120.09987536766145-.008, 36.3497971057915+.405) # lv16 ll


modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
ll_cc = modem_raster.get_model_lower_left_coord(model_center=model_center,
                                                pad_east=12, pad_north=12)
modem_raster.lower_left_corner = (ll_cc[0]-.076, ll_cc[1]+.045)
modem_raster.save_path = save_path
modem_raster.projection = 'WGS84'
modem_raster.rotation_angle = -40.0
modem_raster.write_raster_files()