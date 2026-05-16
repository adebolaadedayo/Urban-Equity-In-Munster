# config.py

# Database Configuration
DB_SETTINGS = {
    "user": "postgres",
    "password": "polarIS123$",
    "host": "localhost",
    "port": "5432",
    "database": "munster_greenspace"
}

# Project Parameters
CITY_NAME = "Münster, Germany"
HEX_AREA_SQM = 100000
TARGET_CRS = 25832 # UTM 32N for area calculations

#File Paths
PATHS = {
    "worldpop_raster": r"C:\ADE\Works\Muenster_GreenSpace\app\data\germany_population.tif",
    "munster_shapefile": r"C:\ADE\Works\Muenster_GreenSpace\app\data\munster_shape\stadtteil_(statistischer_bezirk).shp",
    "log_file": "logs/pipeline.log",
    "data_dir": r"C:\ADE\Works\Muenster_GreenSpace\app\data"
}