SELECT
	MAX(fr_rev_id) AS rev_id
FROM
	flaggedrevs
WHERE
	fr_page_id = %(page_id)s
    AND fr_rev_id < %(rev_id)s;