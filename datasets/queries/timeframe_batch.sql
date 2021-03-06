SELECT DISTINCT
    fr_page_id AS page_id
FROM
    flaggedrevs
INNER JOIN page ON flaggedrevs.fr_page_id = page.page_id
WHERE
    fr_rev_timestamp BETWEEN %(start)s AND %(stop)s
    AND page_namespace=0
LIMIT %(offset)s,%(number)s;
