SELECT DISTINCT
	page_id
FROM
 	page
INNER JOIN flaggedrevs ON page.page_id=flaggedrevs.fr_page_id
WHERE page_namespace=0
ORDER BY RAND()
LIMIT %(num)s;
