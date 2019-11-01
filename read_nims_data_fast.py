# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:03:20 2019

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
import struct
import datetime

# =============================================================================
# constants
# =============================================================================
class NIMS(object):
    """
    read NIMS data
    """
    
    def __init__(self, fn=None):

        self.fn = fn
        self.block_size = 131
        self.sampling_rate = 8 ### samples/second
        self.e_conversion_factor = 2.44141221047903e-06
        self.h_conversion_factor = 0.01
        self.t_conversion_factor = 70
        self.t_offset = 18048
        self._block_dict = {'soh':0,
                            'block_len':1,
                            'status':2,
                            'gps':3,
                            'sequence':4,
                            'elec_temp':(5, 6),
                            'box_temp':(7, 8),
                            'logic':81,
                            'end':130}
        self.info_array = None
        self.data_array = None
        
        self.indices = self.make_index_values()
        
        if self.fn is not None:
            self.read_nims()
        
    def make_index_values(self):
        """
        Index values for the channels recorded
        """
        ### make an array of index values for magnetics and electrics
        indices = np.zeros((8,5), dtype=np.int)
        for kk in range(8):
            ### magnetic blocks
            for ii in range(3):
                indices[kk, ii] = 9 + (kk) * 9 + (ii) * 3
            ### electric blocks
            for ii in range(2):
                indices[kk, 3+ii] = 82 + (kk) * 6 + (ii) * 3
        return indices
        
    def read_header(self, header_list):
        """
        read header information
        """
        
        self.header_dict = {}
        for line in header_list[0:-1]:
            line = line.decode()
            if line.find('>') == 0:
                continue
            elif line.find(':') > 0:
                key, value = line.split(':', 1)
                self.header_dict[key] = value
            elif line.find('<--') > 0:
                value, key = line.split('<--')
                self.header_dict[key] = value  
        self.data_start_byte = header_list[-1].strip()[0:1] 
                
    def read_nims(self, fn=None):
        """
        read nims binary file
        """
        if fn is not None:
            self.fn = fn

        ### load in the entire file, its not too big
        with open(self.fn, 'rb') as fid:
            nims_str = fid.read()

        self.read_header(nims_str[0:1000].split(b'\r'))
        
        data_start_index = nims_str.find(self.data_start_byte)

        ### read full string into an array with all same data type
        data_str = nims_str[data_start_index:]
        
        ### read in GPS strings into a list to be parsed later
        gps_str = [struct.unpack('c', 
                                 data_str[ii*self.block_size+3:ii*self.block_size+4])[0]
                 for ii in range(int(len(data_str)/self.block_size))]
        gps_str = b''.join(gps_str)
        self.gps_list = gps_str.replace(b'\xd9', b'').replace(b'\xc7', b'').split(b'$')
        
        ### read in full string as unsigned integers
        data = np.frombuffer(data_str, dtype=np.uint8)
        
        ### check the size of the data, should have an equal amount of blocks
        if (data.size % self.block_size) == 0:
            data = data.reshape((int(data.size/self.block_size), 
                                 self.block_size))
        else:
            print('odd number of bytes, not even blocks')
        
        ### need to parse the data
        self.info_array = np.zeros(data.shape[0],
                                   dtype=[('soh', np.int),
                                          ('block_len', np.int),
                                          ('status', np.int),
                                          ('gps', np.int),
                                          ('sequence', np.int),
                                          ('elec_temp', np.float),
                                          ('box_temp', np.float),
                                          ('logic', np.int),
                                          ('end', np.int)])    
        
        for key, index in self._block_dict.items():
                    if 'temp' in key:
                        value = ((data[:, index[0]] * 256 + data[:, index[1]]) - \
                                 self.t_offset)/self.t_conversion_factor
                    else:
                        value = data[:, index]
                    self.info_array[key][:] = value
            
            
        self.data_array = np.zeros(data.shape[0]*self.sampling_rate,
                                   dtype=[('hx', np.float),
                                          ('hy', np.float), 
                                          ('hz', np.float),
                                          ('ex', np.float),
                                          ('ey', np.float)])
        
        ### fill the data
        for cc, comp in enumerate(['hx', 'hy', 'hz', 'ex', 'ey']):
            channel_arr = np.zeros((data.shape[0], 8), dtype=np.float)
            for kk in range(self.sampling_rate):
                index = self.indices[kk, cc]
                value = (data[:, index]*256 + data[:, index+1]) * np.array([256]) + \
                        data[:, index+2]
                value[np.where(value > 8388608)] -= 16777216
                channel_arr[:, kk] = value
            self.data_array[comp][:] = channel_arr.flatten()
            
        ### clean things up
        ### I guess that the E channels are opposite phase?
        for comp in ['ex', 'ey']:
            self.data_array[comp] *= -1 
    
    
#### need to align gps stamps
# =============================================================================
# Test
# =============================================================================

nims_fn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\FieldWork\LP_Data\Mnp310a\DATA.BIN"

st = datetime.datetime.now()
nims_obj = NIMS(nims_fn)

et = datetime.datetime.now()

tdiff = et - st
print('Took {0} seconds'.format(tdiff.total_seconds()))
