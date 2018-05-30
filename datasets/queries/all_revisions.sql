SELECT
	rev_id,
	rev_parent_id,
	rev_user_text,
	rev_timestamp,
	rev_page
FROM
	revision
WHERE
	rev_page=%(page_id)s
	AND rev_id > %(from_rev)s
    AND rev_timestamp > 20080507000000 -- FlaggedRevs was enabled on May 6th 2008
ORDER BY rev_timestamp ASC;
