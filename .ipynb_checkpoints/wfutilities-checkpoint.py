import    gzip          # helps us unzip .gz files
import    urllib.request# helps us download files from the internet
import    tempfile      # creates a temporary file that will disappear later
import    xarray as xr  # the best tool to read weather raster files
from datetime import datetime # handles date and time
from datetime import timedelta # Manipulating time

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

# A function that downloads NLDAS data given a product name and a date
def dowloadNLDAS(input_date):
    year_str  = input_date.strftime("%Y")   # "2019"
    month_str = input_date.strftime("%m")   # "05"
    day_str   = input_date.strftime("%d")   # "23"
    hour_str  = input_date.strftime("%H")   # "12"
    minute_str = input_date.strftime("%M")  # "00"

    url = (f"https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_NOAH0125_H.2.0/"
           f"{year_str}/{month_str}/{day_str}/mrms/ncep/FLASH/{flash_product}/"
           f"NLDAS_NOAH0125_H.A{year_str}{month_str}{day_str}.{hour_str}00.020.nc")

    response = urllib.request.urlopen(url)
    compressed_data = response.read()
    
    print(url)
    print(f"   → Got the file! Size: {len(compressed_data):,} bytes (compressed)")
#     #https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_NOAH0125_H.2.0/2019/022/NLDAS_NOAH0125_H.A20190122.1500.020.nc
# # A function that downloads NLDAS data given a product name and a date
# def dowloadNLDAS(input_date):
#     year_str  = input_date.strftime("%Y")   # "2019"
#     month_str = input_date.strftime("%m")   # "05"
#     day_str   = input_date.strftime("%d")   # "23"
#     hour_str  = input_date.strftime("%H")   # "12"
#     minute_str = input_date.strftime("%M")  # "00"

#     day_of_year = input_date.timetuple().tm_yday

#     url = (f"https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_NOAH0125_H.2.0/"
#            f"{year_str}/{day_of_year}/NLDAS_NOAH0125_H.A{year_str}{month_str}{day_str}.{hour_str}00.020.nc")

#     with requests.Session() as session:
#         session.auth = None          # force netrc usage
#         response = session.get(url, timeout=60)
#         response.raise_for_status()

#         data = response.content
    
#     print(url)
#     print(f"   → Got the file! Size: {len(data):,} bytes (compressed)")

# dowloadNLDAS(case_dt)