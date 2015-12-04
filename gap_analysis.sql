-- SIDEWALK GAP ANALYSIS
-- Using street centerlines and existing sidewalks, this script
-- draws possible missing sidewalks. The output table, missing_segment,
-- contains a block identifier, the percentage of the total block length
-- that the segment represents, and the geometry of the segment.

-- The script expects as its inputs three tables--study_area, street, and
-- sidewalk--with the following schemas:

-- CREATE TABLE study_area (
--   gid integer,
--   geom geometry(Polygon)
-- )

-- CREATE TABLE street (
--   gid integer,
--   needs_sidewalk boolean,
--   geom geometry(LineString)
-- )

-- CREATE TABLE sidewalk (
--   gid integer,
--   geom geometry(LineString)
-- )

-- The geometry columns in these tables should use an appropriate projected
-- coordinate system and should have gist-based spatial indices. If the
-- coordinate system uses a spatial unit other than feet, the buffer lengths
-- specified in the first step should be adjusted accordingly.

-- STEP 1: DEFINE BLOCKS
-- A block is defined as the area between streets. The resulting table contains
-- two geometries: a line geometry representing the expected location of
-- sidewalks (25 feet from the street centerlines), and a search area polygon
-- consisting of the area between 1 and 75 feet from the street centerlines.
CREATE TEMPORARY TABLE block AS
-- Create the expected sidewalk line geometry and the search area polygon
-- geometry.
SELECT row_number() OVER () AS gid,
  ST_ExteriorRing(poly.geom) AS line_geom,
  ST_Multi(ST_Difference(
    ST_Buffer(poly.geom, 24), ST_Buffer(poly.geom, -50))) AS search_geom
FROM (
  -- Subtract the street buffers from the study area polygon, creating
  -- block polygons bounded by the street buffers.
  SELECT (ST_Dump(ST_Difference(study_area.geom, buffer.geom))).geom
  FROM study_area
  INNER JOIN (
    -- Create a 25-foot buffer around the street centerlines. This is the
    -- expected sidewalk location.
    SELECT ST_Buffer(ST_Union(street.geom), 25) AS geom
    FROM street
    WHERE street.needs_sidewalk = TRUE
  ) AS buffer
    ON ST_Intersects(study_area.geom, buffer.geom)
) AS poly;

-- Update the geometry type and SRID.
SELECT Populate_Geometry_Columns(TRUE);

-- Create spatial indices on geometry columns.
CREATE INDEX block_line_geom
  ON block
  USING gist (line_geom);

CREATE INDEX block_search_geom
  ON block
  USING gist (search_geom);

-- Update table statistics.
ANALYZE block;

-- STEP 2: FIND BREAKS
-- Breaks are the points where possible segments will be broken and represent
-- a change in the existing sidewalk (i.e., a sidewalk endpoint or a place
-- where the sidewalk leave the search area).
CREATE TEMPORARY TABLE block_break AS
WITH block_sidewalk AS (
  -- Clip sidewalk segments to the search area for each block.
  SELECT block.gid AS block_gid,
    (ST_Dump(ST_Intersection(sidewalk.geom, block.search_geom))).geom
  FROM block
  INNER JOIN sidewalk
    ON block.search_geom && sidewalk.geom
)
-- For each unique sidewalk endpoint, find the location (from 0 to 1, where 0
-- is the start point and 1 is the end point) of the nearest point on the
-- expected sidewalk line for that block.
SELECT DISTINCT single_pt.block_gid,
  ST_LineLocatePoint(block.line_geom, single_pt.geom) AS location
FROM (
  -- Filter endpoints to those that are unique. Endpoints that are shared
  -- with other segments don't represent a break in the sidewalk.
  SELECT sidewalk_pt.block_gid,
    sidewalk_pt.geom
  FROM (
    -- Find the segment endpoints of the clipped sidewalk segments.
    SELECT block_sidewalk.block_gid,
      ST_StartPoint(block_sidewalk.geom) AS geom
    FROM block_sidewalk
    UNION ALL SELECT block_sidewalk.block_gid,
      ST_EndPoint(block_sidewalk.geom) AS geom
    FROM block_sidewalk
  ) AS sidewalk_pt
  GROUP BY sidewalk_pt.block_gid, sidewalk_pt.geom
  HAVING count(*) = 1
) AS single_pt
INNER JOIN block
  ON block.gid = single_pt.block_gid;

-- STEP 3: SPLIT SEGMENTS
-- Split the expected sidewalk segments at the previously identified break
-- locations.
CREATE TEMPORARY TABLE possible_segment AS
-- Add a unique ID column to the segments.
SELECT row_number() OVER () AS gid,
  segment.*
FROM (
  -- Divide the block lines at the break points.
  SELECT segment_info.block_gid,
    segment_info.start_location,
    segment_info.end_location,
    CASE WHEN segment_info.end_location > segment_info.start_location THEN
      -- If the desired segment does not span the block start/end point,
      -- extract the segment from the line.
      ST_LineSubstring(block.line_geom, segment_info.start_location,
        segment_info.end_location)
    ELSE
      -- If the desired segment does not span the block start/end point,
      -- extract the segment from the line.
      ST_MakeLine(
        ST_LineSubstring(block.line_geom, segment_info.start_location, 1.0),
        ST_LineSubstring(block.line_geom, 0.0, segment_info.end_location)
      )
    END AS geom
  FROM (
    -- Set the end location for segments that span the block start/end point.
    SELECT start_end.block_gid,
      start_end.start_location,
      CASE WHEN start_end.end_location IS NULL THEN
        first_value(start_end.start_location)
          OVER (
            PARTITION BY start_end.block_gid
            ORDER BY start_end.start_location
          )
      ELSE start_end.end_location END AS end_location
    FROM (
      -- Identify the segment start and end locations using a window function.
      SELECT block_break.block_gid,
        block_break.location AS start_location,
        lead(block_break.location, 1)
          OVER (
            PARTITION BY block_break.block_gid
            ORDER BY block_break.location
          ) AS end_location
      FROM block_break
    ) AS start_end
  ) AS segment_info
  INNER JOIN block
    ON block.gid = segment_info.block_gid
  -- Add blocks with no break points.
  UNION SELECT block.gid AS block_gid,
    0.0 AS start_location,
    1.0 AS end_location,
    block.line_geom AS geom
  FROM block
  WHERE block.gid NOT IN (
    SELECT DISTINCT block_break.block_gid
    FROM block_break
  )
) AS segment;

-- Update the geometry type and SRID.
SELECT Populate_Geometry_Columns(TRUE);

-- Create a spatial index on the geometry column.
CREATE INDEX possible_segment_geom
  ON possible_segment
  USING gist (geom);

-- Update table statistics.
ANALYZE possible_segment;

-- STEP 4: DRAW SEARCH LINES
-- Search lines are used to determine whether there is an existing sidewalk
-- segment adjacent to the expected sidewalk segment.
CREATE TEMPORARY TABLE segment_searchline AS
-- Identify the closest points to the segment midpoint on the inner and outer
-- rings of the search area. Then draw a line between those points. In cases
-- where the search area has no inner ring (e.g., for very small blocks), use
-- the centroid of the outer ring instead.
SELECT midpoint.gid,
  midpoint.block_gid,
  ST_MakeLine(
    ST_ClosestPoint(block_ring.outer_geom, midpoint.geom),
    CASE WHEN ST_Length(block_ring.inner_geom) > 0 THEN
      ST_ClosestPoint(block_ring.inner_geom, midpoint.geom)
    ELSE
      ST_Centroid(block_ring.outer_geom)
    END
  ) AS geom
FROM (
  -- Find the midpoint of each possible sidewalk segment.
  SELECT possible_segment.gid,
    possible_segment.block_gid,
    ST_LineInterpolatePoint(possible_segment.geom, 0.5) AS geom
  FROM possible_segment
) AS midpoint
INNER JOIN (
  -- Create multi-part line geometries representing the inner and outer rings
  -- of the search area.
  SELECT search_ring.gid,
    ST_Collect(
      CASE WHEN search_ring.ring_type = 0
      THEN search_ring.geom
      ELSE NULL END) AS outer_geom,
    ST_Collect(
      CASE WHEN search_ring.ring_type > 0
      THEN search_ring.geom
      ELSE NULL END) AS inner_geom
  FROM (
    -- Extract rings from the search area polygons.
    SELECT search_part.gid,
      (ST_DumpRings(search_part.geom)).path[1] AS ring_type,
      ST_ExteriorRing((ST_DumpRings(search_part.geom)).geom) AS geom
    FROM (
      -- Break search area multi-part polygons into single-part polygons.
      SELECT block.gid,
        (ST_Dump(block.search_geom)).geom AS geom
      FROM block
    ) AS search_part
  ) AS search_ring
  GROUP BY search_ring.gid
) AS block_ring
  ON midpoint.block_gid = block_ring.gid;

-- Update the geometry type and SRID.
SELECT Populate_Geometry_Columns(TRUE);

-- Create a spatial index on the geometry column.
CREATE INDEX segment_searchline_geom
  ON segment_searchline
  USING gist (geom);

-- Update table statistics.
ANALYZE segment_searchline;

-- STEP 5: IDENTIFY MISSING SEGMENTS
-- Find possible sidewalk segments where the associated search line does not
-- intersect an existing sidewalk. From these missing segments, eliminate
-- obvious false positives: breaks for driveways and streets that do not
-- require sidewalks, and interior loops within small cul-de-sacs.
DROP TABLE IF EXISTS missing_segment;
CREATE TABLE missing_segment AS
-- Find all possible sidewalk segments that have not been eliminated by one
-- of the conditions below.
SELECT possible_segment.gid,
  possible_segment.block_gid,
  -- Determine the decimal percentage of the total block length contained
  -- in this segment.
  CASE WHEN possible_segment.end_location > possible_segment.start_location THEN
    -- For segments that do not cross the block start/end point, the percentage
    -- is the end location minus the start location.
    possible_segment.end_location - possible_segment.start_location
  ELSE
    -- For segments that cross the block start/end point, the percentage is
    -- the portion of the block not between the start and end locations.
    1 - (possible_segment.start_location - possible_segment.end_location)
  END AS block_pct,
  possible_segment.geom
FROM possible_segment
WHERE possible_segment.gid NOT IN (
  -- Remove segments where the search line intersects an existing sidewalk.
  SELECT DISTINCT segment_searchline.gid
  FROM segment_searchline
  INNER JOIN sidewalk
    ON ST_Intersects(segment_searchline.geom, sidewalk.geom)
  -- Remove sidewalk breaks for driveways and other streets that do not
  -- require sidewalks.
  UNION SELECT possible_segment.gid
  FROM possible_segment
  INNER JOIN street
    ON ST_Intersects(street.geom, possible_segment.geom)
    AND ST_Length(possible_segment.geom) < 100
    AND street.needs_sidewalk = FALSE
  -- Remove interior sidewalk loops from small cul-de-sacs.
  UNION SELECT possible_segment.gid
  FROM possible_segment
  WHERE ST_Length(possible_segment.geom) < 200
    AND ST_EndPoint(possible_segment.geom) =
      ST_StartPoint(possible_segment.geom)
);

-- Update the geometry type and SRID.
SELECT Populate_Geometry_Columns(TRUE);

-- Create a spatial index on the geometry column.
CREATE INDEX missing_segment_geom
  ON missing_segment
  USING gist (geom);

-- Update table statistics.
ANALYZE missing_segment;

-- STEP 6: CALCULATE GAP LENGTH RATIO
-- Gap length ratio is the ratio of the length of the missing segment to
-- the combined length of all existing sidewalks within a 1/4-mile buffer
-- around the missing segment. Gap length ratio is inversely related to
-- connectivity. A small gap length ratio indicates a large potential increase
-- in connectivity relative to the cost of filling the gap.

-- Add a new column for gap length ratio.
ALTER TABLE missing_segment
ADD COLUMN gap_length_ratio double precision;

UPDATE missing_segment
SET gap_length_ratio = gap_length.ratio
FROM (
  SELECT missing_segment.gid,
    -- Divide the length of the segment by the length of existing segments
    -- clipped to a 1/4 mile buffer.
    ST_Length(missing_segment.geom)/
      ST_Length(ST_Intersection(
        ST_Buffer(missing_segment.geom, 1320),
        ST_Collect(sidewalk.geom))) AS ratio
  FROM missing_segment
  INNER JOIN sidewalk
    -- Join missing segments to existing segments that are within 1/4 mile.
    ON ST_DWithin(missing_segment.geom, sidewalk.geom, 1320)
  GROUP BY missing_segment.gid, missing_segment.geom
) AS gap_length
WHERE missing_segment.gid = gap_length.gid;
