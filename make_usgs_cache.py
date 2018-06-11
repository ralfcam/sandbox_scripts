# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 16:38:28 2017

@author: jpeacock
"""
#==============================================================================

import os
import time
import datetime
from collections import Counter

import urllib2 as url
import xml.etree.ElementTree as ET

import numpy as np
import scipy.signal as sps
import pandas as pd

import mtpy.usgs.zen as zen
import mtpy.usgs.zonge as zonge
import mtpy.utils.gis_tools as gis_tools
from mtpy.utils.configfile import write_dict_to_configfile

# =============================================================================
# Collect Z3d files
# =============================================================================
class Z3DCollection(object):
    """
    Will collect z3d files into useful arrays and lists
    """   
    
    def __init__(self):
        
        self.fn_list = None
        self.z3d_obj_list = None
        self.save_fn = None
        self._ch_factor = '9.5367431640625e-10'
        self.verbose = True
        self.log_lines = []
        self.chn_order = ['hx','ex','hy','ey','hz']
        self.meta_notes = None
        
    def get_time_blocks(self, z3d_dir):
        """
        organize z3d files into blocks based on start time and sampling rate
        """
        
        fn_list = os.listdir(z3d_dir)
        merge_list = np.array([[fn]+\
                              os.path.basename(fn)[:-4].split('_')
                              for fn in fn_list if fn.endswith('.Z3D')])
                                  
        merge_list = np.array([merge_list[:,0], 
                               merge_list[:,1],  
                               np.core.defchararray.add(merge_list[:,2],
                                                        merge_list[:,3]),
                               merge_list[:,4],
                               merge_list[:,5]])
        merge_list = merge_list.T
                      
        time_counts = Counter(merge_list[:,2])
        time_list = time_counts.keys()
        log_lines = []
        
        return_list = []
        for tt in sorted(time_list):
            block_list = []
            log_lines.append('+'*72+'\n')
            log_lines.append('Files Being Merged: \n')
            time_fn_list = merge_list[np.where(merge_list == tt)[0], 0].tolist()
            for cfn in time_fn_list:
                log_lines.append(' '*4+cfn+'\n')
                block_list.append(os.path.join(z3d_dir, cfn))

            return_list.append(block_list)
            log_lines.append('\n---> Merged Time Series Lengths and Start Time \n')
            log_lines.append('\n')
            
        with open(os.path.join(z3d_dir, 'z3d_merge.log'), 'w') as fid:
            fid.writelines(log_lines)
        
        return return_list
   
    #==================================================
    def check_sampling_rate(self, time_array):
        """
        check to make sure the sampling rate is the same for all channels
        
        Arguments:
        -----------
            **zt_list** : list of Zen3D instances
        
        Outputs:
        --------
            **None** : raises an error if sampling rates are not all the same
            
        """
        
        nz = len(time_array)
        
        df_array = time_array['df']
            
        tf_array = np.zeros((nz, nz))
        
        for jj in range(nz):
            tf_array[jj] = np.in1d(df_array, [df_array[jj]])
        
        false_test = np.where(tf_array==False)
        
        if len(false_test[0]) != 0:
            raise IOError('Sampling rates are not the same for all channels '+\
                          'Check file(s)'+time_array[false_test[0]]['fn'])
            
        return df_array.mean()
        
    #==================================================
    def check_time_series(self, fn_list):
        """
        check to make sure timeseries line up with eachother.
        
        """
        # get number of channels
        n_fn = len(fn_list)
        
        # make an empty array to put things into
        t_arr = np.zeros(n_fn, 
                         dtype=[('comp', 'S3'),
                                ('start', np.int64),
                                ('stop', np.int64),
                                ('fn', 'S140'),
                                ('df', np.float32),
                                ('lat', np.float32),
                                ('lon', np.float32),
                                ('elev', np.float32), 
                                ('ch_azm', np.float32),
                                ('ch_length', np.float32),
                                ('ch_num', np.float32),
                                ('ch_box', 'S6'),
                                ('n_samples', np.int32),
                                ('t_diff', np.int32)])
            
        print('-'*50)
        for ii, fn in enumerate(fn_list):
            z3d_obj = zen.Zen3D(fn)
            z3d_obj.read_z3d()
            
            # convert the time index into an integer
            dt_index = z3d_obj.ts_obj.ts.data.index.astype(np.int64)/10.**9
            
            # extract useful data
            t_arr[ii]['comp'] = z3d_obj.metadata.ch_cmp.lower()
            t_arr[ii]['start'] = dt_index[0]
            t_arr[ii]['stop'] = dt_index[-1]
            t_arr[ii]['fn'] = fn
            t_arr[ii]['df'] = z3d_obj.df
            t_arr[ii]['lat'] = z3d_obj.header.lat
            t_arr[ii]['lon'] = z3d_obj.header.long
            t_arr[ii]['elev'] = z3d_obj.header.alt
            t_arr[ii]['ch_azm'] = z3d_obj.metadata.ch_azimuth
            if 'e' in t_arr[ii]['comp']:
                t_arr[ii]['ch_length'] = z3d_obj.metadata.ch_length
            t_arr[ii]['ch_num'] = z3d_obj.metadata.ch_number
            t_arr[ii]['ch_box'] = int(z3d_obj.header.box_number)
            t_arr[ii]['n_samples'] = z3d_obj.ts_obj.ts.shape[0]
            t_arr[ii]['t_diff'] = int((dt_index[-1]-dt_index[0])*z3d_obj.df)-\
                                      z3d_obj.ts_obj.ts.shape[0]
            try:
                self.meta_notes = z3d_obj.metadata.notes.replace('\r', ' ').replace('\x00', '').rstrip()
            except AttributeError:
                pass

            if self.verbose:
                print '{0} -- {1:<16.2f}{2:<16.2f} sec'.format(z3d_obj.metadata.ch_cmp,
                                                           dt_index[0],
                                                           dt_index[-1])                 

            self.log_lines.append('{0} -- {1:<16.2f}{2:<16.2f} sec'.format(z3d_obj.metadata.ch_cmp,
                                                           dt_index[0],
                                                           dt_index[-1]))
        # cut the array to only those channels with data
        t_arr = t_arr[np.nonzero(t_arr['start'])]
        
        return t_arr
    
    def merge_ts(self, fn_list, decimate=1):
        """
        merge z3d's based on a mutual start and stop time
        """
        meta_arr = self.check_time_series(fn_list)
        df = self.check_sampling_rate(meta_arr)
        
        # get the start and stop times that correlates with all time series
        start = meta_arr['start'].max()
        stop = meta_arr['stop'].min()
        
        # figure out the max length of the array, getting the time difference into
        # seconds and then multiplying by the sampling rate
        max_ts_len = int((stop-start)*df)
        ts_len = min([meta_arr['n_samples'].max(), max_ts_len])
        
        if decimate > 1:
            ts_len /= decimate
        
        ts_db = pd.DataFrame(np.zeros((ts_len, meta_arr.size)),
                             columns=list(meta_arr['comp']),
                             dtype=np.float32)
        
        for ii, m_arr in enumerate(meta_arr):
            z3d_obj = zen.Zen3D(m_arr['fn'])
            z3d_obj.read_z3d()
            
            dt_index = z3d_obj.ts_obj.ts.data.index.astype(np.int64)/10**9
            index_0 = np.where(dt_index == start)[0][0]
            #index_1 = np.where(dt_index == stop)[0][0]
            index_1 = min([ts_len-index_0, z3d_obj.ts_obj.ts.shape[0]-index_0])
            t_diff = ts_len-(index_1-index_0)
            meta_arr[ii]['t_diff'] = t_diff

            if t_diff != 0:
                if self.verbose:
                    print '{0} off by {1} points --> {2} sec'.format(z3d_obj.ts_obj.fn,
                                                                     t_diff,
                                                                     t_diff/z3d_obj.ts_obj.sampling_rate)
                self.log_lines.append('{0} off by {1} points --> {2} sec \n'.format(z3d_obj.ts_obj.fn,
                                                                     t_diff,
                                                                     t_diff/z3d_obj.ts_obj.sampling_rate))
            if decimate > 1:
                 ts_db[:, ii] = sps.resample(z3d_obj.ts_obj.ts.data[index_0:index_1],
                                              ts_len, 
                                              window='hanning')

            else:
                ts_db[m_arr['comp']][0:ts_len-t_diff] = z3d_obj.ts_obj.ts.data[index_0:index_1]

        # reorder the columns        
        ts_db = ts_db[self.get_chn_order]
        
        # return the pandas database and the metadata array 
        return ts_db, meta_arr 
    
    def get_chn_order(self, chn_list):
        """
        get the order of the array according to the components
        """
        
        if len(chn_list) == 5:
            return self.chn_order
        else:
            chn_order = []
            for chn_00 in self.chn_order:
                for chn_01 in chn_list:
                    if chn_00.lower() == chn_01.lower():
                        chn_order.append(chn_00.lower())
                        continue
            
            return chn_order

#==============================================================================
# Need a dummy utc time zone for the date time format
#==============================================================================
class UTC(datetime.tzinfo):
    def utcoffset(self, df):
        return datetime.timedelta(hours=0)
    def dst(self, df):
        return datetime.timedelta(0)
    def tzname(self, df):
        return "UTC"

# =============================================================================
#  Metadata for usgs ascii file
# =============================================================================
class Metadata(object):
    def __init__(self, fn=None, **kwargs):
        self.fn = fn
        self.SurveyID = None
        self.SiteID = None
        self.RunID = None
        self._latitude = None
        self._longitude = None
        self._elevation = None
        self._start_time = None
        self._stop_time = None
        self._sampling_rate = None
        self._n_samples = None
        self.channel_dict = None
        self.MissingDataFlag = '{0:.0e}'.format(1e9)
        self._chn_num = None
        self.CoordinateSystem = None
        self._time_fmt = '%Y-%m-%dT%H:%M:%S %Z'
        self._metadata_len = 30
        
        self._key_list = ['SurveyID',
                          'SiteID',
                          'RunID',
                          'SiteLatitude',
                          'SiteLongitude',
                          'SiteElevation',
                          'AcqStartTime',
                          'AcqStopTime',
                          'AcqSmpFreq',
                          'AcqNumSmp',
                          'Nchan',
                          'CoordinateSystem',
                          'ChnSettings',
                          'MissingDataFlag',
                          'DataSet']
        
        self._chn_settings = ['ChnNum',
                              'ChnID',
                              'InstrumentID',
                              'Azimuth',
                              'Dipole_Length']
        self._chn_fmt = {'ChnNum':'<7',
                         'ChnID':'<6',
                         'InstrumentID':'<13',
                         'Azimuth':'>7.1f',
                         'Dipole_Length':'>14.1f'}

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            
            
    @property
    def SiteLatitude(self):
        return gis_tools.convert_position_float2str(self._latitude)
    
    @SiteLatitude.setter
    def SiteLatitude(self, lat):
        self._latitude = gis_tools.assert_lat_value(lat)
        
    @property
    def SiteLongitude(self):
        return gis_tools.convert_position_float2str(self._longitude)
    
    @SiteLongitude.setter
    def SiteLongitude(self, lon):
        self._longitude = gis_tools.assert_lon_value(lon)
        
    @property
    def SiteElevation(self):
        """
        get elevation from national map
        """  
        # the url for national map elevation query
        nm_url = r"https://nationalmap.gov/epqs/pqs.php?x={0:.5f}&y={1:.5f}&units=Meters&output=xml"

        # call the url and get the response
        response = url.urlopen(nm_url.format(self._longitude, self._latitude))
        
        # read the xml response and convert to a float
        info = ET.ElementTree(ET.fromstring(response.read()))
        info = info.getroot()
        for elev in info.iter('Elevation'):
            nm_elev = float(elev.text) 
        return nm_elev 
        
    @property
    def AcqStartTime(self):
        return self._start_time.strftime(self._time_fmt)
    
    @AcqStartTime.setter
    def AcqStartTime(self, time_string):
        if type(time_string) in [int, np.int64]:
            dt = datetime.datetime.utcfromtimestamp(time_string)
        elif type(time_string) in [str]:
            dt = datetime.datetime.strptime(time_string, self._time_fmt)
        self._start_time = datetime.datetime(dt.year, dt.month, dt.day,
                                             dt.hour, dt.minute, dt.second,
                                             dt.microsecond, tzinfo=UTC())
        
    @property
    def AcqStopTime(self):
        return self._stop_time.strftime(self._time_fmt)
    
    @AcqStopTime.setter
    def AcqStopTime(self, time_string):
        if type(time_string) in [int, np.int64]:
            dt = datetime.datetime.utcfromtimestamp(time_string)
        elif type(time_string) in [str]:
            dt = datetime.datetime.strptime(time_string, self._time_fmt)
        self._stop_time = datetime.datetime(dt.year, dt.month, dt.day,
                                            dt.hour, dt.minute, dt.second,
                                            dt.microsecond, tzinfo=UTC())
    
    @property
    def Nchan(self):
        return self._chn_num
    
    @Nchan.setter
    def Nchan(self, n_channel):
        try:
            self._chn_num = int(n_channel)
        except ValueError:
            print("{0} is not a number, setting Nchan to 0".format(n_channel))
            
    @property
    def AcqSmpFreq(self):
        return self._sampling_rate
    @AcqSmpFreq.setter
    def AcqSmpFreq(self, df):
        self._sampling_rate = float(df)

    @property
    def AcqNumSmp(self):
        return self._n_samples

    @AcqNumSmp.setter
    def AcqNumSmp(self, n_samples):
        self._n_samples = int(n_samples)  

    def read_metadata(self, meta_lines=None):
        """
        read in a meta from the raw string
        """
        chn_find = False
        comp = 0
        self.channel_dict = {}
        if meta_lines is None:
            with open(self.fn, 'r') as fid:
                meta_lines = [fid.readline() for ii in range(self._metadata_len)]
        for ii, line in enumerate(meta_lines):
            if line.find(':') > 0:
                key, value = line.strip().split(':', 1)
                value = value.strip()
                if len(value) < 1 and key == 'DataSet':
                    chn_find = False
                    # return the line that the data starts on that way can
                    # read in as a numpy object or pandas
                    return ii+1
                elif len(value) < 1:
                    chn_find = True
                setattr(self, key, value)
            elif 'coordinate' in line:
                self.CoordinateSystem = ' '.join(line.strip().split()[-2:])
            else:
                if chn_find is True:
                    if 'chnnum' in line.lower():
                        ch_key = line.strip().split()
                    else:
                        line_list = line.strip().split()
                        if len(line_list) == 5:
                            comp += 1
                            self.channel_dict[comp] = {}
                            for key, value in zip(ch_key, line_list):
                                if key.lower() in ['azimuth', 'dipole_length']:
                                    value = float(value)
                                self.channel_dict[comp][key] = value
                        else:
                            print('Not sure what line this is')
                            
    def write_metadata(self):
        """
        Write out metadata in the format of PB
        
        returns a list of lines to write use '\n'.join(lines) to write out
        """
        lines = []
        for key in self._key_list:
            if key in ['ChnSettings']:
                lines.append('{0}:'.format(key))
                lines.append(' '.join(self._chn_settings))
                for chn_key in sorted(self.channel_dict.keys()):
                    chn_line = []
                    for comp_key in self._chn_settings:
                        chn_line.append('{0:{1}}'.format(self.channel_dict[chn_key][comp_key],
                                        self._chn_fmt[comp_key]))
                    lines.append(''.join(chn_line))
            elif key in ['DataSet']:
                lines.append('{0}:'.format(key))
                return lines
            else:
                lines.append('{0}: {1}'.format(key, getattr(self, key)))
        
        return lines


# =============================================================================
# Class for the asc file
# =============================================================================
class USGSasc(Metadata):
    """
    read and write Paul's ascii formatted time series
    """
    
    def __init__(self, **kwargs):
        Metadata.__init__(self)
        self.ts = None
        self.fn = None
        self.station_dir = os.getcwd()
        self.meta_notes = None
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            
    def get_z3d_db(self, fn_list):
        zc_obj = Z3DCollection()
        self.ts, meta_arr = zc_obj.merge_ts(fn_list)
        self.fill_metadata(meta_arr)
        self.meta_notes = zc_obj.meta_notes
        
    def read_mtft24_cfg(self, mtft24_cfg_fn):
        """
        read in a MTFT24 configuration file and fill in meta data
        """
        zm = zonge.ZongeMTFT()
        zm.read_cfg(mtft24_cfg_fn)
        
        # need to update channel dict
        # figure out channel order first
        chn_order = dict([(cc.lower(), ii) for ii, cc in enumerate(zm.Chn_Cmp)])
        for chn in self.channel_dict.keys():
            index = chn_order[chn.lower()]
            if len(zm.Chn_ID[index]) == 4:
                self.channel_dict[chn]['ChnNum'] = zm.Chn_ID[index]
            if int(self.channel_dict[chn]['Azimuth']) != int(zm.Chn_Azimuth[index]):
                self.channel_dict[chn]['Azimuth'] = float(zm.Chn_Azimuth[index])
            if float(self.channel_dict[chn]['Dipole_Length']) != float(zm.Chn_Length[index]):
                if 'e' in chn.lower(): 
                    self.channel_dict[chn]['Dipole_Length'] = float(zm.Chn_Length[index])
        
        
    def fill_metadata(self, meta_arr):
        self.AcqNumSmp = self.ts.shape[0]
        self.AcqSmpFreq = meta_arr['df'].mean()
        self.AcqStartTime = meta_arr['start'].max()
        self.AcqStopTime = meta_arr['stop'].min()
        self.Nchan = self.ts.shape[1]
        self.RunID = 1
        self.SiteLatitude = np.median(meta_arr['lat'])
        self.SiteLongitude = np.median(meta_arr['lon'])
        self.SiteID = os.path.basename(meta_arr['fn'][0]).split('_')[0]
        self.station_dir = os.path.dirname(meta_arr['fn'][0])
        self.channel_dict = dict([(comp.capitalize(),
                                   {'ChnNum':meta_arr['ch_num'][ii],
                                    'ChnID':meta_arr['comp'][ii].capitalize(),
                                    'InstrumentID':meta_arr['ch_box'][ii],
                                    'Azimuth':meta_arr['ch_azm'][ii],
                                    'Dipole_Length':meta_arr['ch_length'][ii],
                                    'n_samples':meta_arr['n_samples'][ii],
                                    'n_diff':meta_arr['t_diff'][ii]})
                                   for ii, comp in enumerate(meta_arr['comp'])])

    def read_asc_file(self, fn=None, str_fmt='%11.7g'):
        if fn is not None:
            self.fn = fn
        st = datetime.datetime.now()    
        data_line = self.read_metadata()
        self.ts = pd.read_csv(self.fn,
                              delim_whitespace=True,
                              skiprows=data_line,
                              dtype=np.float32)
        et = datetime.datetime.now()
        read_time = et-st
        print('Reading took {0}'.format(read_time.total_seconds()))
        
    def convert_electrics(self):
        """
        convert electric fields into mV/km
        """
        
        try:
            self.ts.ex /= (self.channel_dict['Ex']['Dipole_Length']/1000.)
        except AttributeError:
            print('No EX')
            
                
        try:
            self.ts.ey /= (self.channel_dict['Ey']['Dipole_Length']/1000.)
        except AttributeError:
            print('No EY')
        
    def write_asc_file(self, save_fn, chunk_size=1024, str_fmt='%11.7g', 
                       full=True):
        """
        write an ascii file in the USGS archive format
        """
        # get the number of characters in the desired string
        s_num = int(str_fmt[1:str_fmt.find('.')])
        
        # convert electric fields into mV/km
        self.convert_electrics()
        
        print('START --> {0}'.format(time.ctime()))
        st = datetime.datetime.now()
        
        # write meta data first
        meta_lines = self.write_metadata()
        with open(save_fn, 'w') as fid:
            h_line = [''.join(['{0:>{1}}'.format(c.capitalize(), s_num) 
                      for c in self.ts.columns])]
            fid.write('\n'.join(meta_lines+h_line) + '\n')
            
            # write out data
            if full is False:
                out = np.array(self.ts[0:chunk_size])
                out[np.where(out == 0)] = float(self.MissingDataFlag)
                out = np.char.mod(str_fmt, out)
                lines = '\n'.join([''.join(out[ii, :]) for ii in range(out.shape[0])])
                fid.write(lines+'\n')
                print('END --> {0}'.format(time.ctime()))
                et = datetime.datetime.now()
                write_time = et-st
                print('Writing took: {0} seconds'.format(write_time.total_seconds()))
                return 
            
            for chunk in range(int(self.ts.shape[0]/chunk_size)):
                out = np.array(self.ts[chunk*chunk_size:(chunk+1)*chunk_size])
                out[np.where(out == 0)] = float(self.MissingDataFlag)
                out = np.char.mod(str_fmt, out)
                lines = '\n'.join([''.join(out[ii, :]) for ii in range(out.shape[0])])
                fid.write(lines+'\n')
        print('END --> {0}'.format(time.ctime()))
        et = datetime.datetime.now()
        write_time = et-st
        print('Writing took: {0} seconds'.format(write_time.total_seconds()))
        
    def write_station_info_metadata(self):
        """
        write out station info that can later be put into a data base
        
        the data we need is
            - site name
            - site id number
            - lat
            - lon
            - national map elevation
            - hx azimuth
            - ex azimuth
            - hy azimuth
            - hz azimuth
            - ex length
            - ey length
            - start date
            - end date
            - instrument type (lp, bb)
            - number of channels
            
        """
        
        save_fn = os.path.join(self.station_dir, '{0}.cfg'.format(self.SiteID))
        meta_dict = {}
        key = self.SiteID
        meta_dict[key] = {}
        meta_dict[key]['site'] = self.SiteID
        meta_dict[key]['lat'] = self._latitude
        meta_dict[key]['lon'] = self._longitude
        meta_dict[key]['elev'] = self.SiteElevation
        try:
            meta_dict[key]['hx_azm'] = self.channel_dict['Hx']['Azimuth']
            meta_dict[key]['hx_id'] = self.channel_dict['Hx']['ChnNum']
            meta_dict[key]['hx_nsamples'] = self.channel_dict['Hx']['n_samples']
            meta_dict[key]['hx_ndiff'] = self.channel_dict['Hx']['n_diff']
            meta_dict[key]['zen_num'] = self.channel_dict['Hx']['InstrumentID']
        except KeyError:
            meta_dict[key]['hx_azm'] = None
            meta_dict[key]['hx_id'] = None
            meta_dict[key]['hx_nsamples'] = None
            meta_dict[key]['hx_ndiff'] = None
        try:
            meta_dict[key]['hy_azm'] = self.channel_dict['Hy']['Azimuth']
            meta_dict[key]['hy_id'] = self.channel_dict['Hy']['ChnNum']
            meta_dict[key]['hy_nsamples'] = self.channel_dict['Hy']['n_samples']
            meta_dict[key]['hy_ndiff'] = self.channel_dict['Hy']['n_diff']
            meta_dict[key]['zen_num'] = self.channel_dict['Hy']['InstrumentID']
        except KeyError:
            meta_dict[key]['hy_azm'] = None
            meta_dict[key]['hy_id'] = None
            meta_dict[key]['hy_nsamples'] = None
            meta_dict[key]['hy_ndiff'] = None
        try:
            meta_dict[key]['hz_azm'] = self.channel_dict['Hz']['Azimuth']
            meta_dict[key]['hz_id'] = self.channel_dict['Hz']['ChnNum']
            meta_dict[key]['hz_nsamples'] = self.channel_dict['Hz']['n_samples']
            meta_dict[key]['hz_ndiff'] = self.channel_dict['Hz']['n_diff']
            meta_dict[key]['zen_num'] = self.channel_dict['Hz']['InstrumentID']
        except KeyError:
            meta_dict[key]['hz_azm'] = None
            meta_dict[key]['hz_id'] = None
            meta_dict[key]['hy_nsamples'] = None
            meta_dict[key]['hy_ndiff'] = None
        
        try:
            meta_dict[key]['ex_azm'] = self.channel_dict['Ex']['Azimuth']
            meta_dict[key]['ex_id'] = self.channel_dict['Ex']['ChnNum']
            meta_dict[key]['ex_len'] = self.channel_dict['Ex']['Dipole_Length']
            meta_dict[key]['ex_nsamples'] = self.channel_dict['Ex']['n_samples']
            meta_dict[key]['ex_ndiff'] = self.channel_dict['Ex']['n_diff']
            meta_dict[key]['zen_num'] = self.channel_dict['Ex']['InstrumentID']
        except KeyError:
            meta_dict[key]['ex_azm'] = None
            meta_dict[key]['ex_id'] = None
            meta_dict[key]['ex_len'] = None
            meta_dict[key]['ex_nsamples'] = None
            meta_dict[key]['ex_ndiff'] = None
        
        try:
            meta_dict[key]['ey_azm'] = self.channel_dict['Ey']['Azimuth']
            meta_dict[key]['ey_id'] = self.channel_dict['Ey']['ChnNum']
            meta_dict[key]['ey_len'] = self.channel_dict['Ey']['Dipole_Length']
            meta_dict[key]['ey_nsamples'] = self.channel_dict['Ey']['n_samples']
            meta_dict[key]['ey_ndiff'] = self.channel_dict['Ey']['n_diff']
            meta_dict[key]['zen_num'] = self.channel_dict['Ey']['InstrumentID']
        except KeyError:
            meta_dict[key]['ey_azm'] = None
            meta_dict[key]['ey_id'] = None
            meta_dict[key]['ey_len'] = None
            meta_dict[key]['ey_nsamples'] = None
            meta_dict[key]['ey_ndiff'] = None
        
        meta_dict[key]['start_date'] = self.AcqStartTime
        meta_dict[key]['stop_date'] = self.AcqStopTime
        meta_dict[key]['sampling_rate'] = self.AcqSmpFreq
        meta_dict[key]['n_samples'] = self.AcqNumSmp
        meta_dict[key]['n_chan'] = self.Nchan
        
        
        if meta_dict[key]['zen_num'] in [24, 25, 26, 46]:
            meta_dict[key]['collected_by'] = 'USGS'
        else:
            meta_dict[key]['collected_by'] = 'OSU'
        
        # in the old OSU z3d files there are notes in the metadata section
        # pass those on
        meta_dict[key]['notes'] = self.meta_notes
            
        write_dict_to_configfile(meta_dict, save_fn)
        
# =============================================================================
# Test collection
# =============================================================================
#z3d_path = r"d:\Peacock\MTData\iMUSH_Zen_samples\OSU_2015\G016"
z3d_path = r"d:\Peacock\MTData\iMUSH_Zen_samples\OSU_2015\H020_Zen18_dropped_channels"

zc = Z3DCollection()
m = zc.get_time_blocks(z3d_path)

zm = USGSasc()
zm.get_z3d_db(m[0])
zm.read_mtft24_cfg(r"D:\Peacock\MTData\iMUSH_Zen_samples\USGS_2015\mo015\mtft24.cfg")
zm.CoordinateSystem = 'Geomagnetic North'
zm.SurveyID = 'iMUSH'
zm.write_asc_file(os.path.join(z3d_path, "test_imush.asc"), str_fmt='%15.7e',
                  full=False)
zm.write_station_info_metadata()
#k = zc.check_time_series(m[0])
#l = zc.check_sampling_rate(k)
#db, da = zc.merge_ts(m[0])
