import toolforge
import pymysql.cursors
from datasets.reverts import get_all_reverted

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

dataset = []

try:
    with conn.cursor() as cursor:
        # Find all manually approved revisions
        cursor.execute(manually_reviewed, {"page_id": 999397, "row_limit": 5})
        conn.commit()
        result = cursor.fetchall()
        dataset.extend([(item["rev_id"], True) for item in result])

        # Find all candidates for revisions which were not approved, but reverted
        cursor.execute(potentially_reverted, {"page_id": 999397, "row_limit": 5})
        conn.commit()
        result = cursor.fetchall()
        candidates = [item["rev_id"] for item in result]

        # Find all revisions
        cursor.execute(all_revisions, {"page_id": 999397})
        conn.commit()
        result = cursor.fetchall()
        all_revisions = [item["rev_id"] for item in result]
        dataset.extend(get_all_reverted(all_revisions, candidates))

finally:
    conn.close()
