from config import PATHS
from etl.spatial_engine import load_boundary, generate_hexagons, push_to_database, export_local_results
from etl.data_extractor import get_population_counts, get_osm_greenery
from etl.analytics import calculate_green_equity

def run_project():
    print("--- Starting Münster Urban Equity Pipeline ---")
    boundary = load_boundary()
    hex_grid = generate_hexagons(boundary)

    # -- DEBUG CHECK --
    print(f"Type of hex_grid: {type(hex_grid)}")
    if hex_grid is not None:
        print(f"Number of hexagons: {len(hex_grid)}")

    # Get Population
    hex_grid = get_population_counts(hex_grid)

    # Get Greenery
    green_spaces = get_osm_greenery(boundary)

    # Calculate Green Equity
    final_grid = calculate_green_equity(hex_grid, green_spaces)

    # Data Export
    export_local_results(final_grid, "munster_urban_equity_results.gpkg")

    # Push to PostGIS database
    push_to_database(final_grid, "munster_hex_equity")

    
    print("\n================================================")
    print("PIPELINE RUN COMPLETE AND DATABASE SYNCED!")
    print("================================================")

if __name__ ==  "__main__":
    run_project()