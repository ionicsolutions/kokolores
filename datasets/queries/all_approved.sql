SELECT
    fr_rev_id AS stable_rev_id
FROM
    flaggedrevs
WHERE
    fr_page_id=%(page_id)s
    AND fr_rev_timestamp < %(stop)s;