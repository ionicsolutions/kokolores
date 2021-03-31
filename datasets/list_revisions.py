import mwapi
import sys

user_agent = "kokolores list revisions <kokolores.revisions@tools.wmflabs.org>"
session = mwapi.Session("https://de.wikipedia.org",
                         formatversion=2,
                         user_agent=user_agent)
title = sys.argv[1]
print("Title", title, sys.argv)

revisions = {}

rvcontinue = None
while True:
    if rvcontinue is None:
        doc = session.post(action='query', prop='revisions',
                           rvlimit=50, rvprop="timestamp|ids|sha1|user|comment",
                           titles=title)
    else:
        doc = session.post(action='query', prop='revisions',
                           rvlimit=50, rvprop="timestamp|ids|sha1|user|comment",
                           titles=title, rvcontinue=rvcontinue)

    for page_doc in doc['query']['pages']:
        if 'revisions' in page_doc:
            for revision_doc in page_doc['revisions']:
                try:
                    revisions[revision_doc["revid"]] = revision_doc
                except KeyError:
                    continue

    if "batchcomplete" in doc:
        break
    else:
        print("Next batch...")
        rvcontinue = doc["continue"]["rvcontinue"]

next = min(revisions.keys())
while True:
    rev = revisions[next]
    print(next, rev["timestamp"], rev["user"], rev["comment"][:100])

    for id, doc in revisions.items():
        if doc["parentid"] == next:
            next = id
            break
    else:
        print("Error!")
        break
