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

conn = toolforge.connect("dewiki_p", cursorclass=pymysql.cursors.DictCursor)

try:
    with conn.cursor() as cursor:
        # Find all manually approved revisions
        cursor.execute(manually_reviewed, {"page_id": 999397, "row_limit": 5})
        conn.commit()
        result = cursor.fetchall()
        for item in result:
             print((item["rev_id"], True))

        # Find all candidates for revisions which were not approved, but reverted
        cursor.execute(potentially_reverted, {"page_id": 999397, "row_limit": 5})
        conn.commit()
        result = cursor.fetchall()
        for item in result:
             print((item["rev_id"], False))
finally:
    conn.close()
    
