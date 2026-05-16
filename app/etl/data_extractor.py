import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
import osmnx as ox
from config import PATHS, TARGET_CRS, DB_SETTINGS
from logger import setup_logger

# Initialize the modular logger
log = setup_logger("DataExtractor")

def get_population_counts(hex_gdf):

    """
    Extracts population counts from the WorldPop raster
    and adds them to the hexagon GeoDataFrame.
    """
    try:
        log.info(f"Extracting population from: {PATHS['worldpop_raster']}")

        # Open the raster to check its CRS
        with rasterio.open(PATHS['worldpop_raster']) as src:
            raster_crs = src.crs
            log.info(f"Raster CRS detected: {raster_crs}")
        
        # Project hexagons to match the Raster (Temporary WGS84)
        hex_for_stats = hex_gdf.to_crs(raster_crs)

        # Run Zonal Sttaistics
        stats = zonal_stats(
            hex_for_stats,
            PATHS['worldpop_raster'],
            stats = "sum"
        )

        # Convert the list of dictionaries from 'stats' into a clean list of numbers
        # If it is None, we make it 0.0
        pop_values = [round(s['sum'], 2) if s['sum'] is not None else 0.0 for s in stats]

        # Attach pop_values back to GeoDataframe
        hex_gdf['pop_count'] = pop_values

        total_pop = hex_gdf['pop_count'].sum()
        log.info(f"Success! Total Munster Population extracted: {total_pop:,.0f}")

        return hex_gdf

    except Exception as e:
        log.error(f"Population extraction failed: {e}")
        raise

def get_osm_greenery(boundary_gdf):
    """
    Downloads greenery features from OpenStreetMap based on the boundary.
    """
    try:
        log.info("Downloading greenery data from OpenStreetMap...")

        # Define what areas are 'Green'
        tags = {
            "leisure": ["park", "nature_reserve", "garden"],
            "landuse": ["forest", "grass", "meadow", "orchard"]
        }

        # Extract greenery from OSM using the city boundary
        # Also project the boundary back to WGS84 for the sake of download
        boundary_wgs84 = boundary_gdf.to_crs(epsg=4326).unary_union

        green_features = ox.features_from_polygon(boundary_wgs84, tags = tags)

        # Clean and project the greenery data
        # Main focus is on the geometry of the green areas
        #Filter to keep only polygons (remove points and lines)
        green_features = green_features[green_features.geometry.type.isin(['Polygon', 'MultiPolygon'])]
        
        green_features = green_features.to_crs(epsg = TARGET_CRS)

        log.info(f"Successfully downloaded {len(green_features)} green space features.")
        return green_features
    
    except Exception as e:
        log.error(f"OSM extraction failed: {e}")
        raise