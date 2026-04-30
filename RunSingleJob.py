# ===============================
# USER-DEFINED CONFIGURATION
# ===============================

case_date = "2019-05-27"
case_time = "00:00"  # UTC

# Parse it into a datetime object
case_dt = datetime.strptime(case_date + " " + case_time, "%Y-%m-%d %H:%M")

# Run Workflow
runWorkFlow(case_dt)