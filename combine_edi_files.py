# -*- coding: utf-8 -*-
"""
Created on Thu Dec 01 11:27:55 2016

@author: jpeacock
"""

import mtpy.core.mt as mt
import numpy as np
import os

ss = 520

lp_fn = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\med{0}_lp.edi".format(ss)
bb_fn = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\med{0}_bb.edi".format(ss)

mt_lp = mt.MT(lp_fn)
mt_bb = mt.MT(bb_fn)

comb_fn = os.path.join(os.path.dirname(bb_fn), 
                       '{0}_c.edi'.format(mt_bb.station))
if os.path.exists(comb_fn):
    os.remove(comb_fn)

#mt_lp.Tipper.rotate(-90)
#mt_lp.Tipper.tipper *= -1-1j
s, mt_lp.Z.z = mt_lp.Z.remove_ss(reduce_res_factor_x=1.2,
                                 reduce_res_factor_y=1.1)

common_freq = 1./3

lp_index = np.where(mt_lp.Z.freq < common_freq)[0]
bb_index = np.where(mt_bb.Z.freq > common_freq)[0]

comb_freq = np.append(mt_bb.Z.freq[bb_index], 
                      mt_lp.Z.freq[lp_index])
nf = comb_freq.size
comb_z = np.zeros((nf, 2, 2), dtype=np.complex)
comb_z[0:bb_index.size, :, :] = mt_bb.Z.z[bb_index, :, :] 
comb_z[bb_index.size:, :, :] = mt_lp.Z.z[lp_index, :, :] 

comb_z_err = np.zeros((nf, 2, 2), dtype=np.complex)
comb_z_err[0:bb_index.size, :, :] = mt_bb.Z.z_err[bb_index, :, :] 
comb_z_err[bb_index.size:, :, :] = mt_lp.Z.z_err[lp_index, :, :]
 
comb_tip = np.zeros((nf, 2, 2), dtype=np.complex)
comb_tip[0:bb_index.size, :, :] = mt_bb.Tipper.tipper[bb_index, :, :] 
comb_tip[bb_index.size:, :, :] = mt_lp.Tipper.tipper[lp_index, :, :] 

comb_tip_err = np.zeros((nf, 2, 2), dtype=np.complex)
comb_tip_err[0:bb_index.size, :, :] = mt_bb.Tipper.tipper_err[bb_index, :, :] 
comb_tip_err[bb_index.size:, :, :] = mt_lp.Tipper.tipper_err[lp_index, :, :] 


comb_z_obj = mt.MTz.Z(comb_z, comb_z_err, comb_freq)
comb_tip_obj = mt.MTz.Tipper(comb_tip, comb_tip_err, comb_freq)

mt_bb.write_edi_file(new_fn=os.path.join(os.path.dirname(bb_fn),
                                         '{0}_c.edi'.format(mt_bb.station)),
                    new_Z=comb_z_obj,
                    new_Tipper=comb_tip_obj)
                    
mt1 = mt.MT(os.path.join(os.path.dirname(bb_fn),
                                         '{0}_c.edi'.format(mt_bb.station)))
p1 = mt1.plot_mt_response(fig_num=2, plot_tipper='yri')
