import toolforge
import pymysql.cursors

# Load SQL query for all manually approved revisions
# based on https://quarry.wmflabs.org/query/27156
with open("queries/manually_reviewed.sql", "r") as queryfile:
    manually_reviewed = queryfile.read()

# Load SQL query for potentially reverted revisions
# based on https://quarry.wmflabs.org/query/27161
with open("queries/potentially_reverted.sql", "r") as queryfile:
    potentially_reverted = queryfile.read()

# Load SQL query for all revisions of a page
# based on https://quarry.wmflabs.org/query/27173
with open("queries/all_revisions.sql", "r") as queryfile:
    all_revisions = queryfile.read()

conn = toolforge.connect("dewiki_p", cursor=pymysql.cursors.DictCursor)

try:
    with conn.cursor() as cursor:
        cursor.execute(manually_reviewed, {"page_id": 999397, "row_limit": 5000})
        conn.commit()

        result = cursor.fetchall()
        print(result)
finally:
    conn.close()
    
