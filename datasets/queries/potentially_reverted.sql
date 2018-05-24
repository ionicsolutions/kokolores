SELECT 
	rev_id,
	rev_parent,
	rev_timestamp,
	rev_page
FROM (
  SELECT
 	rev_id,
 	rev_parent,
    rev_timestamp,
    rev_page
  FROM
    revision
  WHERE
	rev_page=%(page_id)s
) AS all_revisions
LEFT JOIN (
  SELECT
  	fr_rev_id
  FROM
  	flaggedrevs
  WHERE
    fr_page_id=%(page_id)s
) AS flagged_revisions ON all_revisions.rev_id = flagged_revisions.fr_rev_id
WHERE
	flagged_revisions.fr_rev_id IS NULL
    AND all_revisions.rev_timestamp > 20080507000000 -- FlaggedRevs was enabled on May 6th 2008
LIMIT %(row_limit)s;