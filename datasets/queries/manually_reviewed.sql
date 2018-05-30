SELECT 
    rev_id,
    MAX(stable_rev_id) AS rev_parent,
    rev_timestamp,
    rev_page
FROM (
  SELECT
    fr_rev_id AS rev_id,
    fr_rev_timestamp AS rev_timestamp,
    fr_page_id AS rev_page
  FROM
    flaggedrevs
  WHERE
    fr_flags NOT LIKE '%auto%'
    AND fr_page_id=%(page_id)s
) AS manually_reviewed,
(
  SELECT
    fr_rev_id AS stable_rev_id
  FROM
    flaggedrevs
  WHERE
    fr_page_id=%(page_id)s
) AS all_reviewed
WHERE
    rev_id > stable_rev_id
    AND rev_timestamp > 20080507000000 -- FlaggedRevs was enabled on May 6th 2008
GROUP BY rev_id
LIMIT %(row_limit)s;
