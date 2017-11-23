# -*- coding: utf-8 -*-
"""
Created on Fri Nov 07 09:15:17 2014

@author: jpeacock-pr
"""

import mtpy.utils.shapefiles as shapefiles
import os

dfn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\paul_final_model\imush_modem_data_ef04_tip03.dat"
rfn = r"C:\Users\jpeacock\Documents\iMush\modem_inv\paul_final_model\Z4T3_cov0p2x2_L1E2_NLCG_061.dat"

save_path = r"c:\Users\jpeacock\Documents\iMush\modem_inv"
map_projection = 'WGS84'
theta_r = 0

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print 'Made directory {0}'.format(directory_path)
        
##-----------------------------------------------------------
#--> write phase tensor shape files
pts = shapefiles.PTShapeFile()
pts.projection = map_projection
pts.ellipse_size = 2500

##save files for data
#pts.save_path = os.path.join(save_path, 'imush_pt_data')
#check_dir(pts.save_path)
#pts.write_data_pt_shape_files_modem(dfn, rotation_angle=theta_r)
#
##save files for model response
#pts.save_path = os.path.join(save_path, 'imush_pt_model')
#check_dir(pts.save_path)
#pts.write_resp_pt_shape_files_modem(dfn, rfn, rotation_angle=theta_r)

##save files for data-model
#pts.save_path = os.path.join(save_path, 'imush_pt_residual')
#check_dir(pts.save_path)
#pts.write_residual_pt_shape_files_modem(dfn, rfn, rotation_angle=theta_r)
#
#----------------------------------------------------------------
#--> write tipper information
tps = shapefiles.TipperShapeFile()
tps.arrow_size = 10000
tps.arrow_head_height = 750
tps.arrow_head_width = 600
tps.arrow_lw = 100
tps.projection = map_projection

#save files for data
tps.save_path = os.path.join(save_path, 'imush_tipper_data')
check_dir(tps.save_path)
tps.write_tip_shape_files_modem(dfn, rotation_angle=theta_r)

#save files for response
tps.save_path = os.path.join(save_path, 'imush_tipper_model')
check_dir(tps.save_path)
tps.write_tip_shape_files_modem(rfn, rotation_angle=theta_r)

#save files for response
tps.save_path = os.path.join(save_path, 'imush_tipper_residual')
check_dir(tps.save_path)
tps.write_tip_shape_files_modem_residual(dfn, rfn, rotation_angle=theta_r)
