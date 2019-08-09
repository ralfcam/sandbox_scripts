# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 10:42:51 2019

@author: jpeacock
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors

csv_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\rock_resistivity_summary.csv"

rock_dict = {'fsp':'fsp - Franciscan Serpentinite',
             'fgw':'fgw - Franciscan graywacke',
             'Qtb':'Qtb - basalt Caldwell Pines',
             'fmgw':'fmgw - Franciscan Metagraywacke', 
             'fsrgw': 'fsrgw - Franciscan graywacke Melange',
             'Qls': 'Qls - landslide deposits', 
             'fgs': 'fgs - Franciscan Greenstone',
             'fsch': 'fsch - Franciscan Schist',
             'Qt': 'Qt - terrace deposits', 
             'fch': 'fch - Franciscan Chert',
             'KJgv': 'KJgv - Great Valley Sequence', 
             'Qal': 'Qal - alluvium',
             'fabm': 'Qabm - andesite Bogg Mountain',
             'KJf':'KJf - Franciscan Assemblage', 
             'Qc': 'Qc - Coalluvium',
             'Qdcf': 'Qdcf - rhyodacite Cobb Mountain',
             'Qraf': 'Qraf - rhyolite flows Alder Creek',
             'fmum':'fmum - metamorphic ultra-mafics', 
             'Qf': 'Qf - Fill Deposits', 
             'Jos': 'Jos - Coast Range Ophiolite',
             'Qsc': 'Qsc - silica carbonate',
             'Qdcv':'Qdcv - dacite Cobb Valley',
             'Qvc':'Qvc - rhyodacite flows and domes Cobb Mountain',
             'Qmt':'Qmt - mine tailings',
             'felsite':'felsite',
             'steam':'steam field'}

def gradient_image(ax, extent, cmap_range=(0, 1), data_range=(0, 1),
                   cmap=plt.jet):
    """
    Draw a gradient image based on a colormap.

    Parameters
    ----------
    ax : Axes
        The axes to draw on.
    extent
        The extent of the image as (xmin, xmax, ymin, ymax).
        By default, this is in Axes coordinates but may be
        changed using the *transform* kwarg.
    direction : float
        The direction of the gradient. This is a number in
        range 0 (=vertical) to 1 (=horizontal).
    cmap_range : float, float
        The fraction (cmin, cmax) of the colormap that should be
        used for the gradient, where the complete colormap is (0, 1).
    **kwargs
        Other parameters are passed on to `.Axes.imshow()`.
        In particular useful is *cmap*.
    """
    a, b = cmap_range
    c, d = data_range
    
    grad = np.atleast_2d(np.linspace(c, d, 256))
    im = ax.imshow(grad, extent=extent, interpolation='bicubic',
                   alpha=1, vmin=a, vmax=b, cmap=cmap)
    return im

# =============================================================================
# color bar
# =============================================================================
#red to green to blue
ptcmapdict4 = {'red':  ((0.0, 0.0, 0.65),
                        (0.25, 1.0, 1.0),
                        (0.5, 1.0, 1.00),
                        (0.68,0.0, 0.0),
                        (1.0, 0.0, 0.0)),

               'green': ((0.0, 0.0, 0.0),
                         (0.25, 0.95, 0.95),
                         (0.5, 1.0, 1.0),
                         (0.68, .85, 0.85),
                         (1.0, 0.0, 0.0)),

              'blue':  ((0.0, 0.0, 0.0),
                        (0.25, 0.0, 0.0),
                        (0.5, 1.0, 1.0),
                        (0.68,1.0, 1.0),
                        (1.0, 0.45, 1.0))}
mt_rd2gr2bl = colors.LinearSegmentedColormap('mt_rd2gr2bl', ptcmapdict4, 256)
# =============================================================================
# plot bars on color scale
# =============================================================================
df = pd.read_csv(csv_fn)
        
#xmin, xmax = xlim = 0, 10
#ymin, ymax = ylim = 0, 1

fig = plt.figure(2)
fig.clf()
fig.tight_layout()

ax = fig.add_subplot(1, 1, 1, aspect=.05)
ax.set(xlim=(np.log10(10), np.log10(300)), 
       ylim=(-2, 55))
ax.yaxis.set_visible(False)
ax.set_xlabel('Resistivity ($\Omega \cdot m$)', fontdict={'size':14})
ax.grid(which='major', color=(.25, .25, .25), lw=.75, ls=':')
ax.set_axisbelow(True)
for row in df.itertuples():
    bar_extent = (np.log10(max([1, row.pdf_50_min])), 
                  np.log10(row.pdf_50_max),
                  2*(row.Index + 1),
                  2*(row.Index + 1) + 1.85)
    gradient_image(ax, 
                   bar_extent,  
                   cmap=mt_rd2gr2bl, 
                   cmap_range=(np.log10(1), np.log10(500)), 
                   data_range=(np.log10(max([1, row.pdf_50_min])), np.log10(row.pdf_50_max)))
    ax.plot([np.log10(row.mode), np.log10(row.mode)], 
            [2 * (row.Index + 1), 2 * (row.Index + 1)+1.85],
            'k', lw=2)
    ax.text(np.log10(row.pdf_50_max)+.005,
            2*(row.Index + 1)+1,
            rock_dict[row.rock_type],
            verticalalignment='center', 
            horizontalalignment='left')

gradient_image(ax, 
               (np.log10(1), np.log10(500), -2, 0 ), 
               cmap=mt_rd2gr2bl, 
               cmap_range=(np.log10(1), np.log10(500)), 
               data_range=(np.log10(1), np.log10(500)))

plt.show()

ax.set_aspect(.02)
xticks = np.log10(np.append(np.arange(10, 100, 10), np.arange(100, 400, 100)))
ax.set_xticks(xticks)
xlabels = ['{0:.0f}'.format(xx) for xx in np.round(10**xticks, 0)]
ax.set_xticklabels(xlabels)
fig.tight_layout()
fig.canvas.draw()
    
