-- Create spatial index
DROP INDEX IF EXISTS idx_munster_hex_geom;
CREATE INDEX idx_munster_hex_geom
ON munster_equity_hex
USING GIST (geom);