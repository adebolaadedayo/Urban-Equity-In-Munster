import os
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
from sqlalchemy import create_engine
from config import DB_SETTINGS, HEX_AREA_SQM, TARGET_CRS, PATHS
from logger import setup_logger

# Initialize the modular logger
log = setup_logger("SpatialEngine")

def load_boundary():
   
    """Loads the local Munster shapefile from the config path"""

    try:
        log.info(f"Loading boundary from: {PATHS['munster_shapefile']}")
        boundary = gpd.read_file(PATHS['munster_shapefile'])

        #Ensuring that it is in the correct UTM projection for area calculation
        boundary = boundary.to_crs(epsg= TARGET_CRS)
        return boundary
    except Exception as e:
        log.error(f"Failed to load boundary: {e}")
        raise

def generate_hexagons(boundary_gdf):
    
    """Creates the hexagonal grid based on the area in config"""

    log.info(f"Generating hexagons with area {HEX_AREA_SQM} sqm") 

    # Define the Hexagon dimensions (side length 's')
    # Area of hexagon = (3 * sqrt(3) / 2) * s^2
    s = np.sqrt(HEX_AREA_SQM / (1.5 * np.sqrt(3)))
    w = 1.5 * s         # vertical distance
    h = np.sqrt(3) * s  # horizontal distance

    # Get the total bounds from the provided boundary - min xy and max xy
    bounds = boundary_gdf.total_bounds

    # Generate grid ranges
    cols = np.arange(bounds[0], bounds[2] + h, h)
    rows = np.arange(bounds[1], bounds[3] + w, w)
    
    hexagons = [] 
    
    for x in cols:
        for j, y in enumerate(rows):
            #Shift every other column to create the honeycomb fit
            x_offset = h / 2 if j % 2 == 1 else 0
            p = x + x_offset
            
            #Create the 6 points of the hexagon
            hex_points = [
                (p, y + s),
                (p + h / 2, y + s / 2),
                (p + h / 2, y - s / 2),
                (p, y - s),
                (p - h / 2, y - s / 2),
                (p - h / 2, y + s / 2)
            ]
            hexagons.append(Polygon(hex_points))

    # Convert Hexagon to GeoDataFrame
    hex_gdf = gpd.GeoDataFrame({'geometry': hexagons}, crs = TARGET_CRS)

    # Clip the Hexagon by Munster Boundary
    log.info("Clipping hexagons to study area boundary...")
    munster_geom = boundary_gdf.unary_union
    hex_gdf = hex_gdf[hex_gdf.intersects(munster_geom)].copy()

    # Add a permanent ID column for the hexagon
    hex_gdf['hex_id'] = range(len(hex_gdf))

    log.info(f"Successfully created {len(hex_gdf)} hexagons matching notebook logic")
    return hex_gdf

def push_to_database(gdf, table_name):

    """Connects to PostGIS and saves the GeoDataFrame"""
    
    log.info(f"Creating connection to {DB_SETTINGS['database']} database...")
    
    try:
        # Create the connection strong from config
        conn_url = (
            f"postgresql://{DB_SETTINGS['user']}:{DB_SETTINGS['password']}"
            f"@{DB_SETTINGS['host']}:{DB_SETTINGS['port']}/{DB_SETTINGS['database']}"
        )
        engine = create_engine(conn_url)

        log.info(f"Pushing {len(gdf)} rows to PostGIS table: {table_name}")

        # Save to database
        gdf.to_postgis(table_name, engine, if_exists= 'replace', index= False)

        log.info("Database sync successful!")
    except Exception as e:
        log.error(f"Failed to push to database: {e}")
        raise

def export_local_results(gdf, file_name):
    """Saves the final processed GeoDataFrame to the data directory"""
    try:
        # Create the data directory if it doesn't exist
        os.makedirs(PATHS['data_dir'], exist_ok=True)

        output_path = os.path.join(PATHS['data_dir'], file_name)
        log.info(f"Exporting final results locally to: {output_path}")

        # Save as a GeoPackage
        gdf.to_file(output_path, driver="GPKG")
        log.info("Local file export complete!")
    except Exception as e:
        log.error(f"Failed to export local file: {e}")
        raise