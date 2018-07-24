"""FlaggedRevs API

This API provides functionality which is currently not available through the
MediaWiki API.
"""
import os

import mwapi
import toolforge
from flask import Blueprint, jsonify, request

flagged_api = Blueprint('api', __name__)

SUPPORTED_WIKIS = ["de"]

USER_AGENT = "kokolores API <kokolores.api@wmflabs.org"
sessions = {}

__dir__ = os.path.dirname(__file__)
with open(os.path.join(__dir__, "queries/flagged_parent.sql"),
          "rt") as queryfile:
    FLAGGED_PARENT = queryfile.read()


def _get_session(wiki):
    if wiki not in sessions:
        sessions[wiki] = mwapi.Session(
            "https://{:s}.wikipedia.org".format(wiki),
            user_agent=USER_AGENT)
    return sessions[wiki]


def _get_connection(wiki):
    return toolforge.connect("{:s}wiki_p".format(wiki))


@flagged_api.route("/api/v1/<string:wiki>/parent/<int:rev_id>/",
                   defaults={"page_id": None})
@flagged_api.route("/api/v1/<string:wiki>/parent/<int:rev_id>/<int:page_id>")
def flagged_parent(wiki, rev_id, page_id):
    if wiki not in SUPPORTED_WIKIS:
        return jsonify({"ERROR": "Only %s are supported." % SUPPORTED_WIKIS})

    return jsonify(most_recent_approved(wiki, rev_id, page_id))


@flagged_api.route("/api/v1/<string:wiki>/parent/", methods=["POST"])
def flagged_parents(wiki):
    if wiki not in SUPPORTED_WIKIS:
        return jsonify({"ERROR": "Only %s are supported." % SUPPORTED_WIKIS})

    try:
        rev_ids = request.get_json()["revids"]
    except KeyError:
        return jsonify({"ERROR": "Need to provide a list of revids."})
    else:
        return jsonify(most_recent_approved_many(wiki, rev_ids))


def most_recent_approved(wiki, rev_id, page_id=None):
    if page_id is None:
        session = _get_session(wiki)
        doc = session.post(action="query",
                           revids=[rev_id])
        page_id = int(next(iter(doc["query"]["pages"])))

    conn = _get_connection(wiki)
    try:
        with conn.cursor() as cursor:
            cursor.execute(FLAGGED_PARENT,
                           {"page_id": page_id,
                            "rev_id": rev_id})
            conn.commit()
            parent_id = int(cursor.fetchone()[0])
    except Exception as e:
        return {"ERROR": str(e)}
    else:
        return {"revid": rev_id,
                "pageid": page_id,
                "parentid": parent_id}
    finally:
        conn.close()


def most_recent_approved_many(wiki, rev_ids):
    flagged_parents = {}
    session = _get_session(wiki)
    doc = session.post(action="query",
                       prop=["revisions", "flagged"],
                       revids=rev_ids)
    # TODO: handle query continuation
    for page_id, page_doc in doc["query"]["pages"].items():
        stable_revid = int(page_doc["flagged"]["stable_revid"])

        page_revisions = [int(revision["rev_id"])
                          for revision in page_doc["revisions"]]

        for rev_id in page_revisions:
            if rev_id >= stable_revid:
                flagged_parents[rev_id] = stable_revid
            else:
                flagged_parents[rev_id] = \
                    most_recent_approved(rev_id, page_id)["parentid"]
    return jsonify(flagged_parents)
