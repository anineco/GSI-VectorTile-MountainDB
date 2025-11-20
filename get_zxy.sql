-- Get ZXY tiles for points in geom table at zoom level 15
SET @zoom = 15;
SELECT
  DISTINCT
  CONCAT(
    @zoom,
    '/',
    FLOOR(
      (ST_Longitude(pt) + 180) / 360 * POW(2, @zoom)
    ),
    '/',
    FLOOR(
      (1 - LN(
        TAN(RADIANS(ST_Latitude(pt))) + SQRT(POW(TAN(RADIANS(ST_Latitude(pt))), 2) + 1)
      ) / PI()) / 2 * POW(2, @zoom)
    )
  ) AS zxy
FROM
  geom
ORDER BY zxy;
