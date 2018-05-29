import toolforge
import pymysql.cursors
from reverts import get_all_reverted
import json

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
    fetch_all_revisions = queryfile.read()

with open("queries/random_batch.sql", "r") as queryfile:
    random_batch = queryfile.read()

conn = toolforge.connect("dewiki_p", cursorclass=pymysql.cursors.DictCursor)

try:
    print("Get batch...")
    with conn.cursor() as cursor:
        cursor.execute(random_batch, {"num": 100})
        conn.commit()
        batch = [int(item["page_id"]) for item in cursor.fetchall()]
    print("Prepared batch of %d pages" % len(batch))
    dataset = []

    for page_id in batch:
        print(page_id)

        with conn.cursor() as cursor:
            # Find all manually approved revisions
            cursor.execute(manually_reviewed, {"page_id": page_id,
                                               "row_limit": 5000})
            conn.commit()
            result = cursor.fetchall()
            print("- %d flagged revisions" % len(result))
            dataset.extend([(item["rev_id"], True, item["rev_parent"])
                            for item in result])

            # Find all candidates for revisions which were not approved,
            # but reverted
            cursor.execute(potentially_reverted, {"page_id": page_id,
                                                  "row_limit": 5000})
            conn.commit()
            result = cursor.fetchall()
            candidates = [item["rev_id"] for item in result]

	    # Find all revisions
            cursor.execute(fetch_all_revisions, {"page_id": page_id})
            conn.commit()
            result = cursor.fetchall()
            all_revisions = [item["rev_id"] for item in result]
            reverted = get_all_reverted(all_revisions, candidates)
            print("- %d reverted revisions" % len(reverted))
            dataset.extend(reverted)

finally:
    conn.close()

print("Created dataset of length", len(dataset))
with open("datasets/temp.js", "w") as datafile:
    json.dump(dataset, datafile, indent=4)
