# ===============================
# USER-DEFINED CONFIGURATION
# ===============================

case_date = "2019-05-27"
case_time = "00:00"  # UTC

# Simple bounding box (Iowa region)
lon_min, lon_max = -130, -60 #-97.5, -90.0
lat_min, lat_max = 24,50 #40.0, 45

# Parse it into a datetime object
case_dt = datetime.strptime(case_date + " " + case_time, "%Y-%m-%d %H:%M")

# Run Workflow
runWorkFlow(case_dt)