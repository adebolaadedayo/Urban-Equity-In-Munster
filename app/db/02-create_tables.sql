-- Create table for Munster tessellations
DROP TABLE IF EXISTS munster_equity_hex;
CREATE TABLE IF NOT EXISTS munster_equity_hex (
	id SERIAL PRIMARY KEY,				-- a unique no for every hexagon
	geom geometry(Polygon),				-- the hexagon shape in WGS84 CRS
	pop_count FLOAT,					-- Population value at that location
	green_area FLOAT,					-- Greenery value at that location
	equity_score VARCHAR(50)			-- Either Low/High category, which will be calculated
);