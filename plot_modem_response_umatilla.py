# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 11:58:23 2015

@author: jpeacock-pr
"""

import mtpy.modeling.modem as modem
import os

dfn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\modem_inv\inv_03\um_data_ef03_tec_edit.dat"
rfn = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\modem_inv\inv_03\um_err03_cov03_NLCG_130.dat"
sv_path = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\Report"

data_obj = modem.Data()
data_obj.read_data_file(dfn)

station_list = data_obj.station_locations.station.copy()

pm = modem.PlotRMSMaps(rfn[:-4]+'.res',
                         marker='o',
                         save_path=sv_path,
                         fig_size=[6.95, 5.5],
                         subplot_right=.875)
pm.plot_loop(fig_format='pdf')

pr = modem.PlotResponse(data_fn=dfn, resp_fn=rfn, 
                        plot_type=station_list[0],
                        fig_size=[6, 3.25],
                        ms=2, 
                        subplot_bottom=.12,
                        subplot_left=.07,
                        font_size=5.7,
                        plot_z = False,
                        plot_yn='n')

               
for ss in station_list:
    pr.plot_type = ss
    pr.redraw_plot()
    
    pr.save_figure(save_fn=os.path.join(sv_path, 
                    'Supp_{0}_resp.pdf'.format(ss)),
                    fig_dpi=600)
                    
lines = []
for ii in range(0, data_obj.station_locations.station.size-2, 3):
    s1 = data_obj.station_locations.station[ii]
    s2 = data_obj.station_locations.station[ii+1]
    s3 = data_obj.station_locations.station[ii+2]
    
    lines.append(r'\begin{picture}(1, 1)')
    gline = r'\put(0,-212){\includegraphics[width=.92\textwidth]{'
    gline += 'Supp_{0}_resp.pdf'.format(s1)
    gline += r'}}'
    lines.append(gline)
    
    gline = r'\put(0,-425){\includegraphics[width=.92\textwidth]{'
    gline += 'Supp_{0}_resp.pdf'.format(s2)
    gline += r'}}'
    lines.append(gline)
    
    gline = r'\put(0,-640){\includegraphics[width=.92\textwidth]{'
    gline += 'Supp_{0}_resp.pdf'.format(s3)
    gline += r'}}'
    lines.append(gline)
    lines.append(r'\end{picture}')
    lines.append(r'\newpage')
    lines.append('')
    
with open(os.path.join(sv_path, "figure_lines.txt"), 'w') as fid:
    fid.write('\n'.join(lines))