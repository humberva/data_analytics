import os
import socket
import time
import sys

print("Starting Python job")

# Show where the job is running
hostname = socket.gethostname()
pid = os.getpid()

print(f"Running on compute node: {hostname}")
print(f"Process ID (PID): {pid}")

# Check if this is running as part of a job array
task_id = os.environ.get("SGE_TASK_ID", "not an array job")
print(f"SGE task ID: {task_id}")

# Pretend to do some computation
print("Doing some work...")
time.sleep(10)

print("Job completed successfully")