# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import simplekml as skml
import os

csv_fn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\umatilla_reservation_mt_sites.csv"

with open(csv_fn, 'r') as fid:
    csv_lines = fid.readlines()

                    

kml_obj = skml.Kml()


for line in csv_lines[1:]:
    csv_list = line.strip().split(',')
    if len(csv_list) < 3:
        break
#    station = 'HF{0:02}'.format(int(csv_list[0].split()[-1]))
    station = 'UM{0}{1:02}'.format(csv_list[0][0], int(csv_list[0][1:]))
    lat = float(csv_list[1])
    lon = float(csv_list[2])
    pnt = kml_obj.newpoint(name=station, 
                           coords=[(lon, lat, 0.0)])
    pnt.style.labelstyle.color = skml.Color.white
    pnt.style.labelstyle.scale = .8
    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/dir_60.png'
    pnt.style.iconstyle.scale = .8

#kml_obj.save(csv_fn[:-4]+'.kml')
kml_obj.save(os.path.join(os.path.dirname(csv_fn), 
                          'umatilla_reservation_mt_sites.kml'))
    
            
            
