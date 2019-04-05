# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 15:03:12 2019

@author: jpeacock
"""

import numpy as np
from mtpy.modeling import modem

dfn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_08\mp_basin_test.dat"

noise = 5./100.

d_obj = modem.Data()
d_obj.read_data_file(dfn)

for d_arr in d_obj.data_array:
    d_arr['z_err'][:] = 0
    for ii in range(2):
        for jj in range(2):
            noise_real = 1 + np.random.random(d_arr['z'].shape[0]) * noise *\
                         (-1)**(np.random.randint(0, 3, d_arr['z'].shape[0]))
            noise_imag = 1 + np.random.random(d_arr['z'].shape[0]) * noise *\
                         (-1)**(np.random.randint(0, 3, d_arr['z'].shape[0]))
            

            zero_index = np.where(d_arr['z'][:, ii, jj] == 0.0)
            d_arr['z'][:, ii, jj].real *= noise_real
            d_arr['z'][:, ii, jj].imag *= noise_imag
            d_arr['z'][zero_index] = 0.0
            
d_obj.error_type_z = 'eigen_floor'
d_obj.error_value_z = 3.0
d_obj.write_data_file(fn_basename='mp_basin_test_noisy_02.dat',
                      elevation=True,
                      fill=False)
            