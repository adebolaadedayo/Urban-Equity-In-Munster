import os
from logger import setup_logger

# 1. Print exactly where Python thinks we are
print(f"Current Working Directory: {os.getcwd()}")

# 2. Try to trigger the logger
try:
    log = setup_logger("DebugCheck")
    log.info("Checking for the log folder...")
    
    if os.path.exists('logs'):
        print("Success! The 'logs' folder was created in this directory.")
    else:
        print("Still no folder. We need to check the path logic in logger.py.")
except Exception as e:
    print(f"An error occurred: {e}")