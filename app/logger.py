import logging
import os

def setup_logger(name):
    """Function to setup logger"""

    # Ensures that the 'logs' folder exists
    if not os.path.exists('app/logs'):
        os.makedirs('app/logs')
    
    # Create the Logger object
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Define the .log file
    file_handler = logging.FileHandler('app/logs/pipeline.log')

    # Define the Format (Time - Module Name - Message)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
    
    return logger