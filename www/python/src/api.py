import toolforge
import mwapi
import os

USER_AGENT = "kokolores API <kokolores.api@wmflabs.org"

__dir__ = os.path.dirname(__file__)

session = mwapi.Session("https://de.wikipedia.org",
                        user_agent=USER_AGENT)

with open(os.path.join(__dir__, "queries/flagged_parent.sql"), "rt") as queryfile:
    FLAGGED_PARENT = queryfile.read()


def _get_connection():
    return toolforge.connect("dewiki_p")


def most_recent_approved_many(rev_ids):
    flagged_parents = {}
    # When kokolores is used for actual review work,
    # the most recent approved revision will be the
    # stable revision of the page which is available
    # through the API
    doc = session.post(action="query",
                       prop=["revisions", "flagged"],
                       revids=rev_ids)

    for page_id, page_doc in doc["query"]["pages"].items():
        stable_revid = int(page_doc["flagged"]["stable_revid"])
        page_revisions = [int(revision["rev_id"])
                          for revision in page_doc["revisions"]]

        for rev_id in page_revisions:
            if rev_id >= stable_revid:
                flagged_parents[rev_id] = stable_revid
            else:
                # Since we already know the page in question, we
                # can conveniently use that information for the
                # database query
                flagged_parents[rev_id] = most_recent_approved(rev_id, page_id)
    return flagged_parents


def most_recent_approved(rev_id, page_id):
    conn = _get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(FLAGGED_PARENT,
                           {"page_id": int(page_id),
                            "rev_id": rev_id})
            conn.commit()
            return int(cursor.fetchone())
    finally:
        conn.close()
