import geopandas as gpd
from config import TARGET_CRS
from logger import setup_logger

log = setup_logger("Analytics")

def calculate_green_equity(hex_gdf, green_gdf):
    """
    Calculates the square meters of green space per capita for each hexagon.
    """
    try:
        log.info("Starting spatial intersection for green equity math...")

        # Ensure everything is explicitly in the preferred metric UTM CRS
        hex_gdf = hex_gdf.to_crs(epsg=TARGET_CRS)
        green_gdf = green_gdf.to_crs(epsg=TARGET_CRS)

        # Perform a Spatial Intersection
        # This breaks down large parks into pieces that match our hexagon boundaries
        log.info("Intersecting hexagons with green space polygons...")
        intersections = gpd.overlay(hex_gdf, green_gdf, how = 'intersection')

        # Calculate the area of the green pieces (in square meters)
        intersections['green_area_sqm'] = intersections.geometry.area

        # Group by hex_id to sum up all green space pieces inside the same hexagon
        log.info("Aggregating green areas per hexagon...")
        green_totals = intersections.groupby('hex_id')['green_area_sqm'].sum().reset_index()

        # Merge the totals back into our master hexagon grid
        hex_gdf = hex_gdf.merge(green_totals, on='hex_id', how='left')
        hex_gdf['green_area_sqm'] = hex_gdf['green_area_sqm'].fillna(0.0)

        # Calculate Green Space per Capita
        # Also, avoid division-by-zero errors for empty hexagons using a safe function
        log.info("Calculating Green Space per Capita...")

        def compute_per_capita(row):
            if row['pop_count'] <= 0:
                return 0.0
            return round(row['green_area_sqm'] / row['pop_count'], 2)
        hex_gdf['green_per_capita'] = hex_gdf.apply(compute_per_capita, axis=1)

        log.info("Green equity metrics computed successfully!")
        return hex_gdf
    
    except Exception as e:
        log.error(f"Analytics computation failed: {e}")
        raise