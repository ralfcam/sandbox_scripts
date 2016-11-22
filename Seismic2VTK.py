# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 17:28:04 2014

@author: jpeacock
"""

import os
from evtk.hl import pointsToVTK
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll

sfn = r"/home/jpeacock/Documents/LP_and_BF_earthquake_locations.csv"
east_0 = 329740.62
north_0 = 4193509.70

s_array = np.loadtxt(sfn, delimiter=',', 
                     dtype = [('year', np.float),
                              ('month', np.float),
                              ('day', np.float),
                              ('lat', np.float),
                              ('lon', np.float),
                              ('depth', np.float),
                              ('mag', np.float)],
                     skiprows=1)
                  
east = np.zeros(s_array.shape[0])
north = np.zeros(s_array.shape[0])

for ii, ss in enumerate(s_array):
    zz, ee, nn = utm2ll.LLtoUTM(23, ss['lat'], ss['lon'])
    east[ii] = (ee-east_0)/1000.
    north[ii] = (nn-north_0)/1000.


x = north.copy()
y = east.copy()
z = s_array['depth'].copy()
mag = s_array['mag'].copy()


for xx, yy, zz, mm in zip(x, y, z, mag):
    print 'N={0:.2f}, E={1:.2f}, Z={2:.2f}, M={3:.2f}'.format(xx, yy, zz, mm)
    
pointsToVTK(r"/home/jpeacock/Documents/mb_LP_locations", x, y, z, 
            data={'mag':mag, 'depth':z})
            


