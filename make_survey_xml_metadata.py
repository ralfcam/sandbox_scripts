# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 14:11:43 2018

@author: jpeacock
"""

import xml.etree.cElementTree as ET
import xml.dom.minidom as minidom

# =============================================================================
# Input data
# =============================================================================
authors = ['Jared R. Peacock', 'Kevin Denton', 'Dave Ponce']
year = '2018'
title = 'Magnetotelluric data from Mountain Pass, California'
doi_url = 'https://doi.org/10.5066/F7610XTR'
journal_citation = {'author': authors,
                    'title':title,
                    'journal':'Geosphere',
                    'date':'20190101',
                    'issue':'submitted',
                    'volume':'22',
                    'doi_url':'https://doi.org/10.5066/F7610XTR'}
abstract = 'abstract'
purpose = 'survey purpose'
supplement_info = 'in case something goes wrong or needs more explanation'
survey_begin = '20160505'
survey_end = '20160512'
survey_extent = [-120, -118, 39, 37]

science_center = 'GMEGSC'
program = 'MRP'

sc_dict = {'GGGSC': 'Geology, Geophysics, and Geochemistry Science Center',
           'GMEGSC': 'Geology, Minerals, Energy, and Geophysics Science Center'}
program_dict = {'MRP': 'Mineral Resources Program',
               'VHP': 'Volcano Hazards Program'}

keywords_general = [sc_dict[science_center],
                    science_center,
                    program_dict[program],
                    program, 
                    'magnetotellurics',
                    'MT',
                    'time series',
                    'impedance',
                    'apparent resistivity',
                    'phase', 
                    'tipper']

keywords_thesaurus = ['Earth magnetic field',
                      'Geophysics',
                      'Electromagnetic surveying']

locations = ['Primm',
             'Mountain Pass']

use_constraint = 'There is no guarantee concerning the accuracy of the data. '+\
                 'Any user who modifies the data is obligated to describe the '+\
                 'types of modifications they perform. Data have been checked '+\
                 'to ensure the accuracy. If any errors are detected, please '+\
                 'notify the originating office. The U.S. Geological Survey '+\
                 'strongly recommends that careful attention be paid to the '+\
                 'metadata file associated with these data. Acknowledgment of '+\
                 'the U.S. Geological Survey would be appreciated in products '+\
                 'derived from these data. User specifically agrees not to '+\
                 'misrepresent the data, nor to imply that changes made were '+\
                 'approved or endorsed by the U.S. Geological Survey. Please '+\
                 'refer to https://www2.usgs.gov/laws/privacy.html for the '+\
                 'USGS disclaimer.'
                 
submitter = {'name': 'Jared R. Peacock',
             'org': 'U.S. Geological Survey',
             'address': 'Bldg 2, MS 989, 345 Middlefield Rd.',
             'city': 'Menlo Park',
             'state': 'CA',
             'postal': '94125',
             'phone':'650-329-4833',
             'email': 'jpeacock@usgs.gov',
             'country': 'USA'}
funding_source = 'Mineral Resources Program'

complete_warning = 'Data set is considered complete for the information '+\
                   'presented, as described in the abstract. Users are '+\
                   'advised to read the rest of the metadata record '+\
                   'carefully for additional details.'
                   
horizonal_acc = 'Spatial locations were determined from hand-held global '+\
                'positioning system (GPS) devices. In general, the GPS units '+\
                'used by field scientists recorded sample locations to '+\
                'within 100 feet (30 meters) of the true location. The '+\
                'locations were verified using a geographic information '+\
                'system (GIS) and digital topographic maps.'
                
vert_acc = 'Elevations were determined from USGS, The National Map, Bulk '+\
           'Point Query Service based on the USGS 3DEP (3D elevation program) '+\
           '1/3 arc-second layer (10-meter). Vertical accuracy was not '+\
           'assessed for this specific dataset. The overall absolute '+\
           'vertical accuracy of the seamless DEMs within the conterminous '+\
           'United States (2013), expressed as the root mean square error '+\
           '(RMSE) of 25,310 reference points, was 1.55 meters (USGS, '+\
           '2014 - http://dx.doi.org/10.3133/ofr20141008). The vertical '+\
           'accuracy varies across the U.S. as a result of differences in '+\
           'source DEM quality, terrain relief, land cover, and other factors.'

processing = 'The transfer function estimates provided in the *.edi files and '+\
            'displayed in the *.png file were constructed by selecting '+\
            'optimal TF estimates at each period from a suite of data runs. '+\
            'High (500 Hz), mid (50 Hz), and low (6.25 Hz) frequency broadband '+\
            'recordings provided TF estimates for 10-100 Hz, 1-10 Hz, and '+\
            '0.001-1 Hz, respectively. Where available, long period (8 Hz) MT'+\
            'recordings provided TF estimates for periods from 0.001-0.1 Hz '+\
            '(10-11,000 seconds). A select few stations have only long period'+\
            'recordings available, in which case TF estimates are provided for'+\
            'periods 0.001-1 Hz. So-called optimal TFs were selected based on'+\
            'examination of phase slope, smooth curve assumptions, and '+\
            'operator discretion.'
# =============================================================================
# main element
# =============================================================================
metadata = ET.Element('metadata')

# =============================================================================
# ID information
# =============================================================================
idinfo = ET.SubElement(metadata, 'idinfo')

citation = ET.SubElement(idinfo, 'citation')
citeinfo = ET.SubElement(citation, 'citeinfo')
for author in authors:
    ET.SubElement(citeinfo, 'origin').text = author
ET.SubElement(citeinfo, 'pubdate').text = year
ET.SubElement(citeinfo, 'title').text = title
ET.SubElement(citeinfo, 'geoform').text = 'ASCII, shapefile, image'

pubinfo = ET.SubElement(citeinfo, 'pubinfo')
ET.SubElement(pubinfo, 'pubplace').text = 'Menlo Park, CA'
ET.SubElement(pubinfo, 'publish').text = 'U. S. Geological Survey' 

ET.SubElement(citeinfo, 'onlink').text = doi_url
# journal publication
if journal_citation:
    journal = ET.SubElement(citeinfo, 'lworkcit')
    jciteinfo = ET.SubElement(journal, 'citeinfo')
    for author in journal_citation['author']:
        ET.SubElement(jciteinfo, 'origin').text = author
    ET.SubElement(jciteinfo, 'pubdate').text = journal_citation['date']
    ET.SubElement(jciteinfo, 'title').text = journal_citation['title']
    ET.SubElement(jciteinfo, 'geoform').text = 'Publication'
    serinfo = ET.SubElement(jciteinfo, 'serinfo')
    ET.SubElement(serinfo, 'sername').text = journal_citation['journal']
    ET.SubElement(serinfo, 'issue').text = journal_citation['volume']
    
    jpubinfo = ET.SubElement(jciteinfo, 'pubinfo')
    ET.SubElement(jpubinfo, 'pubplace').text = 'Menlo Park, CA'
    ET.SubElement(jpubinfo, 'publish').text = 'U. S. Geological Survey'
    
    ET.SubElement(jciteinfo, 'onlink').text = journal_citation['doi_url']
    
# description
description = ET.SubElement(idinfo, 'descript')
ET.SubElement(description, 'abstract').text = abstract
ET.SubElement(description, 'purpose').text = purpose
ET.SubElement(description, 'supplinf').text = supplement_info

# dates covered
time_period = ET.SubElement(idinfo, 'timeperd')
time_info = ET.SubElement(time_period, 'timeinfo')
dates = ET.SubElement(time_info, 'rngdates')
ET.SubElement(dates, 'begdate').text = survey_begin
ET.SubElement(dates, 'enddate').text = survey_end
ET.SubElement(time_info, 'current').text = 'Ground condition'

# status
status = ET.SubElement(idinfo, 'status')
ET.SubElement(status, 'progress').text = 'Complete'
ET.SubElement(status, 'update').text = 'As needed'
 
# extent
extent = ET.SubElement(idinfo, 'spdom')
bounding = ET.SubElement(extent, 'bounding')
for ext, name in zip(survey_extent, ['westbc', 'eastbc', 'northbc', 'southbc']):
    ET.SubElement(bounding, name).text = '{0:.1f}'.format(ext)
    
### keywords
keywords = ET.SubElement(idinfo, 'keywords')
t1 = ET.SubElement(keywords, 'theme')
ET.SubElement(t1, 'themekt').text = 'None'
for kw in keywords_general:
    ET.SubElement(t1, 'themekey').text = kw     

# categories
t2 = ET.SubElement(keywords, 'theme')
ET.SubElement(t2, 'themkt').text = 'ISO 19115 Topic Categories'
ET.SubElement(t2, 'themekey').text = 'GeoscientificInformation'

# USGS thesaurus
t3 = ET.SubElement(keywords, 'theme')
ET.SubElement(t3, 'themekt').text = 'USGS Thesaurus'
for kw in keywords_thesaurus:
    ET.SubElement(t3, 'themekey').text = kw

# places
place = ET.SubElement(keywords, 'place')
ET.SubElement(place, 'placekt').text = 'Geographic Names Information System (GNIS)'
for loc in locations:
    ET.SubElement(place, 'placekey').text = loc
    
## constraints
ET.SubElement(idinfo, 'accconst').text = 'None'
ET.SubElement(idinfo, 'useconst').text = use_constraint

### contact information
ptcontact = ET.SubElement(idinfo, 'ptcontac')
contact_info = ET.SubElement(ptcontact, 'cntinfo')
c_perp = ET.SubElement(contact_info, 'cntperp')
ET.SubElement(c_perp, 'cntper').text = submitter['name']
ET.SubElement(c_perp, 'cntorg').text = submitter['org']
c_address = ET.SubElement(contact_info, 'cntaddr')
ET.SubElement(c_address, 'addrtype').text = 'Mailing and physical'
for key in ['address', 'city', 'state', 'postal', 'country']:
    ET.SubElement(c_address, key).text = submitter[key]
    
# funding source
ET.SubElement(idinfo, 'datacred').text = funding_source

# =============================================================================
# Data quality
# =============================================================================
data_quality = ET.SubElement(metadata, 'dataqual')

accuracy = ET.SubElement(data_quality, 'attracc')
ET.SubElement(accuracy, 'attraccr').text = 'No formal attribute accuracy '+\
                                           'tests were conducted.'
ET.SubElement(data_quality, 'logic').text = 'No formal logical accuracy tests'+\
                                            ' were conducted.'
ET.SubElement(data_quality, 'complete').text = complete_warning

# accuracy
position_acc = ET.SubElement(data_quality, 'posacc')
h_acc = ET.SubElement(position_acc, 'horizpa')
ET.SubElement(h_acc, 'horizpar').text = horizonal_acc
v_acc = ET.SubElement(position_acc, 'vertacc')
ET.SubElement(v_acc, 'vertaccr').text = vert_acc

# lineage
lineage = ET.SubElement(data_quality, 'lineage')
processing_step_01 = ET.SubElement(lineage, 'procstep')
ET.SubElement(processing_step_01, 'procdesc').text = processing
ET.SubElement(processing_step_01, 'procdate').text = year 
# =============================================================================
# Spatial reference
# =============================================================================
spref = ET.SubElement(metadata, 'spref')

horizontal_sys = ET.SubElement(spref, 'horizontal_sys')
h_geographic = ET.SubElement(horizontal_sys, 'geograph')
ET.SubElement(h_geographic, 'latres').text = '0.0197305745'
ET.SubElement(h_geographic, 'longres').text = '0.0273088247'
ET.SubElement(h_geographic, 'geogunit').text = 'Decimal seconds'

h_geodetic = ET.SubElement(horizontal_sys, 'geodetic')
ET.SubElement(h_geodetic, 'horizdn').text = 'D_WGS_1984'
ET.SubElement(h_geodetic, 'ellips').text = 'WGS_1984'
ET.SubElement(h_geodetic, 'semiaxis').text = '6378137.0'
ET.SubElement(h_geodetic, 'denflat').text = '298.257223563'



eainfo = ET.SubElement(metadata, 'eainfo')
distinfo = ET.SubElement(metadata, 'distinfo')
metainfo = ET.SubElement(metadata, 'metainfo')

# =============================================================================
# write out xml
# =============================================================================
xmlstr = minidom.parseString(ET.tostring(metadata, 'utf-8')).toprettyxml(indent="    ", encoding='UTF-8')
with open(r"d:\Peacock\MTData\test.xml", 'w') as fid:
    fid.write(xmlstr)