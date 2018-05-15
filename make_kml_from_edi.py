# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import simplekml as skml
import mtpy.core.mt as mt
import os

edi_path = r"d:\Peacock\MTData\Camas\EDI_Files_birrp\Edited\Rotated_13_deg\Camas_EDI_Files_new"

edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi')>0]
                    

kml_obj = skml.Kml()


for edi in edi_list:
    mt_obj = mt.MT(edi)
    pnt = kml_obj.newpoint(name=mt_obj.station, 
                           coords=[(mt_obj.lon, mt_obj.lat, mt_obj.elev)])
    pnt.style.labelstyle.color = skml.Color.white
    pnt.style.labelstyle.scale = .8
    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/dir_60.png'
    pnt.style.iconstyle.scale = .8

kml_obj.save(os.path.join(edi_path, "camas_mt_stations_2018.kml"))
    
            
            
