# -*- coding: utf-8 -*-
"""
Created on Fri Nov 07 09:15:17 2014

@author: jpeacock-pr
"""

import mtpy.utils.shapefiles as shapefiles
import os

dfn = r"c:\Users\jpeacock\Documents\SaudiArabia\inversions\sa_modem_data_err03_tip03_gn.dat"
rfn = r"c:\Users\jpeacock\Documents\SaudiArabia\inversions\MEDWL0p4O_NLCG_091.dat"

save_path = r"c:\Users\jpeacock\Documents\SaudiArabia\inversions"
map_projection = 'WGS84'
theta_r = 0

def check_dir(directory_path):
    if os.path.isdir(directory_path) is False:
        os.mkdir(directory_path)
        print 'Made directory {0}'.format(directory_path)
        
#-----------------------------------------------------------
#--> write phase tensor shape files
pts = shapefiles.PTShapeFile()
pts.projection = map_projection
pts.ellipse_size = 2800

#save files for data
#pts.save_path = os.path.join(save_path, 'SA_GIS_PT_Data_GN')
#check_dir(pts.save_path)
#pts.write_data_pt_shape_files_modem(dfn, rotation_angle=theta_r)

#save files for model response
#pts.save_path = os.path.join(save_path, 'GIS_PT_Response_GN')
#check_dir(pts.save_path)
#pts.write_resp_pt_shape_files_modem(dfn, rfn, rotation_angle=theta_r)
#
##save files for data-model
#pts.save_path = os.path.join(save_path, 'GIS_PT_Residual_GN')
#check_dir(pts.save_path)
#pts.write_residual_pt_shape_files_modem(dfn, rfn, rotation_angle=theta_r)

#----------------------------------------------------------------
#--> write tipper information
tps = shapefiles.TipperShapeFile()
tps.arrow_size = 20000
tps.arrow_head_height = 350
tps.arrow_head_width = 200
tps.arrow_lw = 100
tps.projection = map_projection

#save files for data
#tps.save_path = os.path.join(save_path, 'SA_GIS_Tip_Data_GN')
#check_dir(tps.save_path)
#tps.write_tip_shape_files_modem(dfn, rotation_angle=theta_r)

#save files for response
#tps.save_path = os.path.join(save_path, 'GIS_Tip_Resp_GN')
#check_dir(tps.save_path)
#tps.write_tip_shape_files_modem(rfn, rotation_angle=theta_r)

#save files for response
tps.save_path = os.path.join(save_path, 'GIS_Tip_Residual_GN')
check_dir(tps.save_path)
tps.write_tip_shape_files_modem_residual(dfn, rfn, rotation_angle=theta_r)
