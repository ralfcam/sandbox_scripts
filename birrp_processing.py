# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 12:32:29 2016

@author: jpeacock
"""

import os
import shutil
import mtpy.usgs.zen_processing as zp

#==============================================================================
# local parameters
#==============================================================================
coil_calibration_path = r"/home/jpeacock/Documents/processing/Ant_calibrations"
birrp_path = r"/home/jpeacock/Documents/birrp/birrp52_4pcs16e9pts"
local_path = r"/mnt/hgfs/MTData/MB"
copy_edi_path = local_path
fn_copy = False

if not os.path.exists(local_path):
    os.mkdir(local_path)
#==============================================================================
# Need to copy from the external hard drive first, cause paths are too long
#==============================================================================
hd_path = r"/media/jpeacock/My Passport/WD SmartWare.swstor/IGSWMBWGLTGG032/Volume.b5634234.da89.11e2.aa2b.806e6f6e6963/MT/MB"

# station to process
station = 'mb28'
rr_station = 'mb02'
 
#==============================================================================
# Copy Z3D files to local folder
#==============================================================================
local_station_path = os.path.join(local_path, station)
if not os.path.exists(local_station_path):
    os.mkdir(local_station_path)
    
if rr_station is not None:
    rr_local_station_path = os.path.join(local_path, rr_station)
    if not os.path.exists(rr_local_station_path):
        os.mkdir(rr_local_station_path)

if fn_copy is True:
    # copy all .z3d files to a local station folder
    fn_count = 0
    station_hd_path = os.path.join(hd_path, station)
    for z3d_fn in os.listdir(station_hd_path):
        if z3d_fn.lower().endswith('.z3d'):
            fn_copy_path = os.path.join(local_station_path, z3d_fn)
            if os.path.exists(fn_copy_path) is True:
                continue
            fn_hd_path = os.path.join(hd_path, station, z3d_fn)
            shutil.copy(fn_hd_path, fn_copy_path)
            fn_count += 1
    
    print 'Copied {0} .z3d files to {1}'.format(fn_count, local_station_path)
    
    if rr_station is not None:
        # copy all .z3d files to a local station folder
        fn_count = 0
        rr_station_hd_path = os.path.join(hd_path, rr_station)
        for z3d_fn in os.listdir(rr_station_hd_path):
            if z3d_fn.lower().endswith('hx.z3d') or z3d_fn.lower().endswith('hy.z3d'):
                fn_copy_path = os.path.join(rr_local_station_path, z3d_fn)
                if os.path.exists(fn_copy_path) is True:
                    continue
                fn_hd_path = os.path.join(hd_path, rr_station, z3d_fn)
                shutil.copy(fn_hd_path, fn_copy_path)
                fn_count += 1
        
        print 'Copied {0} .z3d files to {1}'.format(fn_count, local_station_path)
    
    else:
        rr_local_station_path = None
    
#==============================================================================
# Process data
#==============================================================================
b_param_dict = {'c2threshb':.45,
                'c2threshe':.45,
                'c2thresh1':.45,
                'ainuin':.9995,
                'ainlin':.0001,
                'nar':5}


zp_obj = zp.Z3D_to_edi(station_dir=local_station_path,
                       rr_station_dir=rr_local_station_path)
zp_obj.birrp_exe = birrp_path
zp_obj.coil_cal_path = coil_calibration_path

plot_obj, comb_edi_fn = zp_obj.process_data(df_list=[4096, 16],
                                            num_comp=5,
                                            notch_dict={4096:{},
                                                        256:None,
                                                        16:None},
                                            max_blocks=2,
                                            sr_dict={4096:(1000., 25),
                                                     256:(24.999, .126), 
                                                     16:(.125, .0001)},
                                            birrp_param_dict=b_param_dict)
                                            
cp_edi_fn = os.path.join(copy_edi_path, station+'.edi')
shutil.copy(comb_edi_fn, cp_edi_fn)
print '--> Copied {0} to {1}'.format(comb_edi_fn, cp_edi_fn)