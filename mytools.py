# Let's import the needed libraries
import    urllib.request# helps us download files from the internet
import    gzip          # helps us unzip .gz files
import    tempfile      # creates a temporary file that will disappear later
import    xarray as xr  # the best tool to read weather raster files
from datetime import datetime # handles date and time
from datetime import timedelta # Manipulating time
import numpy as np               # for arrays and math (np = nickname)
import matplotlib.pyplot as plt  # main plotting tool (plt = nickname)
import cartopy.crs as ccrs       # map projections
import cartopy.feature as cfeature  # add states, coastlines, etc.
import numpy.ma as ma            # mask/hide bad values
from metpy.plots import ctables  # official radar colors
import matplotlib.colors as mcolors
import os
import requests

# Core scientific Python stack
import pandas as pd
import rasterio
import rioxarray as rxr
from rasterio.enums import Resampling
import geopandas as gpd

# NLDAS Access
import earthaccess

# Image / segmentation utilities
from scipy import ndimage

# Graphics
# FLASH PLOTTING FUNCTION
def plot_FLASH(c_ax,map_extent,flash_product,dataArray,reports,sub_title):
    # Color - 
    all_products = {'unitq':{'label':r'Unit Q ($m^3/s.km^2$)', 'graphpars':{'clims':[0,20], 'clevs':[0,1,2,4,6,10,20], 'colors':['grey', 'lightgrey', 'yellow', 'orange', 'red', 'purple']}},
                'soilsat':{'label':r'Soil Saturation (%)', 'graphpars':{'clims':[0,100], 'clevs':[0,25,50,75,85,95,100], 'colors':['lightgrey', 'grey', 'green', 'yellow', 'orange', 'purple']}},
                   'nldas':{'label':r'Soil Moisture Content ($kg/m^2$)', 'graphpars':{'clims':[0,1000], 'clevs':[0,200,400,600,800,1000], 'colors':['lightgrey', 'grey', 'yellow', 'green', 'blue']}}}

    # FLASH UNIT Q
    ax = c_ax
    
    ax.set_extent(map_extent, crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE, linewidth=2)
    ax.add_feature(cfeature.BORDERS, linewidth=1)
    ax.add_feature(cfeature.STATES, linewidth=0.5)

    clevs = all_products[flash_product]['graphpars']['clevs']
    colors = all_products[flash_product]['graphpars']['colors']
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(clevs, cmap.N)

    dataArray = dataArray.where(dataArray >= 0)
    
    # Create colored mesh
    mesh = dataArray.plot.pcolormesh(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        norm=norm,
        add_colorbar=False
    )

    ax.scatter(
        reports.LON,
        reports.LAT,
        color="red",
        s=40,
        marker="o",
        edgecolor="black",
        label="Local Storm Reports",
        transform=ccrs.PlateCarree()
    )

    # Add colorbar (legend) to explain colors
    cb = plt.colorbar(mesh, ax=ax, orientation='horizontal', pad=0.05, aspect=50)
    cb.set_label(all_products[flash_product]['label'])  # label explains what the numbers mean

    # Add title at the top
    ax.set_title(sub_title, fontsize=14)

# Download LSRs
def getLSRs(file_name,case_dt,buffer_in_days,lat_lb,lat_ub,lon_lb,lon_ub):
    # This is the web address (API) we will ask for data
    base_url = 'https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py'
    
    # We will look for LSRs using a -6 hours + 6 hours window of the case study date
    start_dt = case_dt - timedelta(days=buffer_in_days)
    end_dt = case_dt + timedelta(days=buffer_in_days)
    
    # These are our choices (like filling out a form)
    params = {
        # 'state': 'IA',                   # Only Iowa
        'sts': start_dt.strftime('%Y-%m-%dT%H:%M:%SZ'), #'2024-05-01T00:00:00Z',   # Start time (change these dates!)
        'ets': end_dt.strftime('%Y-%m-%dT%H:%M:%SZ'), #'2024-07-07T23:59:59Z',   # End time
        'fmt': 'csv'                     # We want CSV format
    }
    
    # Choose a name for our file
    # file_name = 'lsr_list.csv'
    file_path = os.path.join(os.getcwd(), file_name)   # full path on your computer
    
    # print(f"Trying to download data for {date_range} ...")
    
    # Ask the website (make the request)
    try:
        response = requests.get(base_url, params=params, timeout=15)
        
        # Did it work?
        if response.status_code == 200:
            # Get the text content
            text = response.text.strip()
            
            # Check if they said "no data"
            if len(text) < 1 or "NO DATA" in text.upper():
                print("→ No storm reports found for these dates.")
            else:
                # Save it to a file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text)
                print(f"→ Success! File saved here: {file_path}")
                print(f"   File size: {os.path.getsize(file_path) / 1024:.1f} KB")
        else:
            print(f"→ Error! Status code: {response.status_code}")
    except:
        print("Something went wrong with the Web request. Using previously downloaded file.")
    
    # Check if the file really exists
    if not os.path.exists(file_path):
        print("No file found. Did Step 2 work?")
    else:
        print(f"Reading file: {file_name}\n")
        
        # Read the CSV into a table (called DataFrame)
        df = pd.read_csv(
            file_path,
            header=0,               # first row = column names
            on_bad_lines='skip',    # skip bad lines if any
            encoding='utf-8'
        )
        
    # Filter LSRs to only show FLASH FLOODS
    # Change this line to try different types!
    wanted_type = 'FLASH FLOOD'          # ← you can change this

    # Filter: keep only rows where TYPETEXT matches wanted_type
    filtered = df[(df['TYPETEXT'] == wanted_type) & 
    (df['LAT'] >= lat_lb) & 
    (df['LAT'] <= lat_ub) &
    (df['LON'] >= lon_lb) & 
    (df['LON'] <= lon_ub)]

    print(f"Showing reports where TYPETEXT = '{wanted_type}'")
    print(f"Found {len(filtered)} matching reports\n")

    if len(filtered) > 0:
        print(filtered[['VALID2', 'CITY', 'COUNTY', 'TYPETEXT', 'MAG']].head(8))
    else:
        print("→ No reports of this type in the selected time period.")

    # Generate a column of datetimes
    filtered["VALID_dt"] = pd.to_datetime(filtered["VALID"],format="%Y%m%d%H%M")

    return filtered

# Hard-coded Auxiliary Data to convert NLDAS soil to FLASH
def loadAuxiliaryData():
    # Load in the Depth-to-Bedrock layer used in FLASH to determine Maximum Soil Depth (cm)
    with rasterio.open("RockDepth_1km_mrms_grid.tif") as src:
        soil_depth = src.read(1)        # NumPy array
        transform = src.transform
        crs = src.crs
        nodata = src.nodata

    # Load in the Effective Porosity layer used in FLASH to determine Maximum Water Capacity
    with rasterio.open("Effective_Porosity_FLASH_MRMS_1km.tif") as src:
        soil_eff_porosity = src.read(1)        # NumPy array
        # transform = src.transform
        # crs = src.crs
        # nodata = src.nodata

    return soil_depth, soil_eff_porosity

# Read NLDAS file
def readNLDAS(case_dt):
    # Login (only once per machine)
    earthaccess.login(persist=True)

    # Download ONE real file
    results = earthaccess.search_data(
        short_name="NLDAS_NOAH0125_H",
        version="2.0",
        temporal=case_dt.strftime("%Y-%m-%d %H:%M"), 
        count=1)

    print(f"Found {len(results)} granule")

    files = earthaccess.download(results, "./nldas_data/")
    local_file = files[0]
    # print("File:", local_file)

    # Open with xarray
    ds_nldas = xr.open_dataset(local_file, engine="netcdf4")

    return ds_nldas

# Convert NLDAS soil data to FLASH-like layer
def nldas2FLASH(nldas_layer,flash_layer,soil_depth_layer,soil_eff_porosity_layer):
    # Transform NLDAS layers to MRMS-FLASH grid conventions
    # 0 - 200 cm
    soil200cm_nldas_mrmsgrid = nldas2mrmsGrid(nldas_layer["SoilM_0_200cm"],flash_layer)
    # 0 - 100 cm
    soil100cm_nldas_mrmsgrid = nldas2mrmsGrid(nldas_layer["SoilM_0_100cm"],flash_layer)
    
    # Combine both NLDAS soil layers considering soil depth
    # Initialize the combined layer with the 100-cm layer. All pixels with soil depth > 200 cm get the 0-200cm values
    soil_nldas_mrmsgrid = xr.where(
        soil_depth_layer > 200,
        soil200cm_nldas_mrmsgrid.isel(time=0),
        soil100cm_nldas_mrmsgrid.isel(time=0))
    
    # Pixels with soil depth between 100 and 200 cm get the weighted average
    mask_mid = (soil_depth_layer > 100) & (soil_depth_layer <= 200)
    soil_interp = soil100cm_nldas_mrmsgrid.isel(time=0) + (soil_depth_layer - 100) * (soil200cm_nldas_mrmsgrid.isel(time=0) - soil100cm_nldas_mrmsgrid.isel(time=0)) / 100.0
    soil_nldas_mrmsgrid = xr.where(
        mask_mid,
        soil_interp,
        soil_nldas_mrmsgrid
    )
    
    # Water density
    rho_water = 1000 # kg m-3
    
    # Convert Soil moisture content kg m-2 to an estimate of Soil Saturation (%)
    theta = soil_nldas_mrmsgrid / (rho_water * soil_depth_layer * 0.01) # theta = Volumetric soil moisture
    nldas_soil_flash_saturation = (theta / soil_eff_porosity_layer) * 100

    return nldas_soil_flash_saturation, soil_nldas_mrmsgrid

# Convert to FLASH grid
def nldas2mrmsGrid(nldas_layer,flash_layer):
    nldas_layer = nldas_layer.rename({"lon": "x", "lat": "y"})

    # Activate rioxarray
    nldas_layer = nldas_layer.rio.set_spatial_dims(x_dim="x", y_dim="y")
    nldas_layer = nldas_layer.rio.write_crs("EPSG:4326")
    nldas_layer = nldas_layer.rio.write_transform()
    
    # Reproject / resample
    warped_nldas_layer = nldas_layer.rio.reproject(
        "EPSG:4326",
        resolution=0.01,
        resampling=Resampling.bilinear        
    )
    
    # Get bounding box of reference raster
    minx, miny, maxx, maxy = flash_layer.rio.bounds()
    
    nldas_mrmsgrid = warped_nldas_layer.rio.reproject_match(flash_layer)

    return nldas_mrmsgrid

# A function that downloads FLASH data given a product name and a date
def downloadFLASH(flash_product,flash_date):
    year_str  = flash_date.strftime("%Y")   # "2019"
    month_str = flash_date.strftime("%m")   # "05"
    day_str   = flash_date.strftime("%d")   # "23"
    hour_str  = flash_date.strftime("%H")   # "12"
    minute_str = flash_date.strftime("%M")  # "00"
    
    url = (f"https://mtarchive.geol.iastate.edu/"
           f"{year_str}/{month_str}/{day_str}/mrms/ncep/FLASH/{flash_product}/"
           f"{flash_product}_00.00_{year_str}{month_str}{day_str}-{hour_str}0000.grib2.gz")

    response = urllib.request.urlopen(url)
    compressed_data = response.read()
    
    print(url)
    print(f"   → Got the file! Size: {len(compressed_data):,} bytes (compressed)")
    
    print("Starting to unzip and load the radar file...")
    
    # We create a temporary file on your computer.
    # This file will hold the unzipped version.
    with tempfile.NamedTemporaryFile(suffix=".grib2") as temp_file:
    
        # ────────────────
        # Part A: Unzip (decompress) the file we downloaded
        # ────────────────
        unzipped_data = gzip.decompress(compressed_data)
        
        print(f"   → Unzipped! New size = {len(unzipped_data):,} bytes")
    
        # Write the unzipped bytes into our temporary file
        temp_file.write(unzipped_data)
        
        # flush() = "make sure everything is really written to disk now"
        # (very important before reading the file)
        temp_file.flush()
        
        print(f"   → Unzipped file saved temporarily at: {temp_file.name}")
    
        # ────────────────
        # Part B: Read the weather data with xarray 
        # ────────────────
        data_in = xr.load_dataarray(
            temp_file.name,             # where the file is
            engine='cfgrib',            # special tool for weather GRIB files
            decode_timedelta=True       # helps with time information
        )

    # Process the downloaded data
    lons = data_in.longitude           # east-west positions (longitudes)
    lats = data_in.latitude            # north-south positions (latitudes)
    refl = data_in.values              # FLASH variable in each grid cell — the main data
    
    flash_layer = data_in.assign_coords(
        longitude=(((data_in.longitude + 180) % 360) - 180)
    ).sortby("longitude")
    
    flash_layer = flash_layer.rename({"longitude": "x", "latitude": "y"})
    flash_layer = flash_layer.rio.set_spatial_dims("x", "y")
    flash_layer = flash_layer.rio.write_crs("EPSG:4326")
    flash_layer = flash_layer.rio.write_nodata(-9999)
    flash_layer = flash_layer.rio.write_transform()

    return flash_layer