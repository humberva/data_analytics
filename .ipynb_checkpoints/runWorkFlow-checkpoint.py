from sys import argv
import mytools as mt
from datetime import datetime

# *********** USER DEFINED SETTINGS ***********
# Case study date
case_datetime = argv[1] #"2019-05-27 00:00"

# LSR search window
time_buffer_days = 6/24 #6 hours in days

# Simple bounding box
lon_min, lon_max = -130, -60 
lat_min, lat_max = 24, 50
# *********** END OF USER DEFINED SETTINGS ***********

# Parse it into a datetime object
case_dt = datetime.strptime(case_datetime, "%Y-%m-%d %H:%M")

## FLASH UNIT Q Layer
flash_unitq = mt.downloadFLASH("CREST_MAXUNITSTREAMFLOW",case_dt)

## FLASH SOILSAT Layer
flash_soilsat = mt.downloadFLASH("CREST_MAXSOILSAT",case_dt)

## Download NLDAS
ds_nldas = mt.readNLDAS(case_dt)

# Load auxiliary data
soil_depth, soil_eff_porosity = mt.loadAuxiliaryData()

# Convert NLDAS to FLASH-like NLDAS
nldas_soil_flashlike_saturation, soil_nldas_over_mrmsgrid = mt.nldas2FLASH(ds_nldas,flash_unitq,soil_depth,soil_eff_porosity)

# Download LSRs
file_name_local = 'lsr_list.csv'
lsr_reports = mt.getLSRs(file_name_local,case_dt,time_buffer_days,lat_min,lat_max,lon_min,lon_max)

# Create a 4-panel figure
fig, axs = mt.plt.subplots(
    2, 2, figsize=(12, 8),
    subplot_kw={"projection": mt.ccrs.PlateCarree()},
    constrained_layout=True
)

# Define general graphic settings
map_extent_for_graph = [lon_min, lon_max, lat_min, lat_max]

# FLASH UNIT Q
mt.plot_FLASH(axs[0,0],map_extent_for_graph,'unitq',flash_unitq, lsr_reports, 'FLASH Maximum Unit Streamflow Layer')

# FLASH SOIL SATURATION
mt.plot_FLASH(axs[0,1],map_extent_for_graph,'soilsat',flash_soilsat,  lsr_reports, 'FLASH Maximum Soil Saturation Layer')

# NLDAS SOIL MOISTURE
mt.plot_FLASH(axs[1,0],map_extent_for_graph,'nldas',soil_nldas_over_mrmsgrid,  lsr_reports, 'NLDAS Soil Moisture Content Layer')

# NLDAS SOIL SATURATION (FLASH Like)
mt.plot_FLASH(axs[1,1],map_extent_for_graph,'soilsat',nldas_soil_flashlike_saturation,  lsr_reports, 'NLDAS FLASH-like Soil Saturation Layer')

# Save as Figure
mt.plt.savefig('FLASH_Soil_Analysis_for_' + case_dt.strftime('%Y%m%d%H%M') + '.png', dpi=150)