SELECT
    fr_rev_id as rev_id
FROM
    flaggedrevs
WHERE
    fr_page_id=%(page_id)s
    AND fr_rev_id > %(from_rev)s
    AND fr_rev_timestamp BETWEEN %(start)s AND %(stop)s;
