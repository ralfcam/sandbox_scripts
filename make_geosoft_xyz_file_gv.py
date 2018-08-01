# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:25:26 2016

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import mtpy.utils.gis_tools as gis_tools
import numpy as np
import matplotlib.pyplot as plt

#mfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_final_err05_cov04_NLCG_040.rho"
#dfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_modem_data_ef05.dat"

#mfn = r"c:\Users\jpeacock\Documents\Geothermal\GraniteSprings\modem_inv\inv_02_tip\gs_prm_err03_tip02_cov03_NLCG_129.rho"
mfn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\modem_inv\inv_02\gv_tip02_cov03_NLCG_031.rho"
dfn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\modem_inv\inv_02\gv_modem_data_ef07_tip02.dat"
save_root = 'gv'
rot_angle = 0.0

#--> read model file
mod_obj = modem.Model()
mod_obj.read_model_file(mfn)

#--> get center position
#model_center = (40.227213, -118.927443)
model_center = (38.772697, -118.149196)
c_east, c_north, c_zone = gis_tools.project_point_ll2utm(model_center[0],
                                                         model_center[1], 
                                                         'WGS84')



#--> set padding
east_pad = 8
north_pad = 8
z_pad = np.where(mod_obj.grid_z > 30000)[0][0]

cos_ang = np.cos(np.deg2rad(rot_angle))
sin_ang = np.sin(np.deg2rad(rot_angle))
rot_matrix = np.matrix(np.array([[cos_ang, sin_ang], 
                                 [-sin_ang, cos_ang]]))

#--> write model xyz file
lines = ['# model_type = electrical resistivity',
         '# model_location = Gabbs Valley, NV',
         '# model_author = J Peacock',
         '# model_organization = U.S. Geological Survey',
         '# model_date = 2017-11-29',
         '# model_datum = WGS84',
         '# model_program = ModEM',
         '# model_rms = 1.6']
lines.append('# north (m) east(m) depth(m) resistivity (Ohm-m)')
             
utm_east = mod_obj.grid_east[east_pad:-east_pad] #+ c_east-200.-2500
utm_north = mod_obj.grid_north[north_pad:-north_pad]# + c_north+200.-2500
for kk, zz in enumerate(mod_obj.grid_z[0:z_pad]):
    for jj, yy in enumerate(utm_east):
        for ii, xx in enumerate(utm_north):
            
            n_east = yy
            n_north = xx
            
            # rotate data
            n_coords = np.array([n_east, n_north])
            new_coords = np.array(np.dot(rot_matrix, n_coords))

            lines.append('{0:>12.1f}{1:12.1f}{2:12.1f}{3:12.2f}'.format(
                          new_coords[0, 1], 
                          new_coords[0, 0], 
                          zz, 
                          mod_obj.res_model[ii, jj, kk]))

save_fn = os.path.join(os.path.dirname(mfn), '{0}_resistivity_relative_coord.xyz'.format(save_root))
with open(save_fn, 'w') as fid:
    fid.write('\n'.join(lines))
    
print 'Wrote file {0}'.format(save_fn)


## test to make sure its properly oriented

d_obj = modem.Data()
d_obj.read_data_file(dfn)

# write data coordinates in model coordinates
d_list = ['station,rel_east, rel_north']
for d_arr in d_obj.data_array:
    d_list.append('{0},{1:.2f},{2:.2f}'.format(d_arr['station'],
                                               d_arr['rel_east'],
                                               d_arr['rel_north']))
with open(save_fn[:-4]+'stations_.csv', 'w') as fid:
    fid.write('\n'.join(d_list))


plot_x, plot_y = np.meshgrid(utm_east, utm_north)
fig = plt.figure(1)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect='equal')
im = ax.pcolormesh(plot_x, plot_y, 
                   np.log10(mod_obj.res_model[north_pad:-north_pad, 
                                      east_pad:-east_pad,
                                      4]),
                    cmap='jet_r',
                    vmin=0,
                    vmax=2.5)
cb = plt.colorbar(im, ax=ax)

ax.scatter(d_obj.station_locations.rel_east, d_obj.station_locations.rel_north, 
           marker='v', c='k', s=25)
ax.set_xlabel('Easting (m)')
ax.set_ylabel('Northing (m)')

plt.show()