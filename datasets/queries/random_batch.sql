SELECT
	page_id
FROM
	page
ORDER BY RAND()
LIMIT %(num)s;