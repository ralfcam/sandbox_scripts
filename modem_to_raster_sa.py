# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:37:19 2015

@author: jpeacock-pr
"""

import mtpy.utils.array2raster as a2r
import os


model_fn = r"c:\Users\jpeacock\Documents\SaudiArabia\modem_inv\inv_n30w\med_z03_t02_c03_164.rho"

save_path = r"c:\Users\jpeacock\Documents\SaudiArabia\modem_inv\inv_n30w\med_raster"
#model_center = (39.756403, 24.342190)
model_center = (39.759, 24.338)

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print 'Made directory {0}'.format(directory_path)
        
check_dir(save_path)

#ll_cc = (-120.09987536766145-.008, 36.3497971057915+.405) # lv16 ll


modem_raster = a2r.ModEM_to_Raster()
modem_raster.model_fn = model_fn
ll_cc = modem_raster.get_model_lower_left_coord(model_center=model_center,
                                                pad_east=5, pad_north=5)
modem_raster.lower_left_corner = (ll_cc[0]+.375, ll_cc[1]-.08)
modem_raster.save_path = save_path
modem_raster.projection = 'WGS84'
modem_raster.rotation_angle = 30.0
modem_raster.write_raster_files()