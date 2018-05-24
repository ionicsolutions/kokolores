import mwapi
import mwreverts

from itertools import islice

my_agent = 'kokolores dataset creator <kokolores.datasets@tools.wmflabs.org>'
session = mwapi.Session('https://de.wikipedia.org',
                        formatversion=2,
                        user_agent=my_agent)


# based on https://github.com/mediawiki-utilities/python-mwapi/blob/master/demo_queries.py
def get_content_by_revids(revids, batch=50):
    revids_iter = iter(revids)
    while True:
        batch_ids = list(islice(revids_iter, 0, batch))
        if len(batch_ids) == 0:
            break
        else:
            doc = session.post(action='query', prop='revisions',
                               revids=batch_ids, rvprop='ids|sha1|user')

            for page_doc in doc['query']['pages']:
                if 'revisions' in page_doc:
                    for revision_doc in page_doc['revisions']:
                        print(revision_doc)
                        yield (revision_doc['sha1'], {"rev_id" : revision_doc['revid'], "user" : revision_doc["user"]})


def get_reverted_revisions(revids):
    return [revision for revision in get_content_by_revids(revids)]


# based on https://github.com/wiki-ai/editquality/blob/master/ipython/reverted_detection_demo.ipynb
def get_all_reverted(revids, candidates):
    revisions = list(get_content_by_revids(revids))
    dataset = []

    for reverting, reverteds, reverted_to in mwreverts.detect(revisions, radius=5):
        if reverteds is not None:
            for candidate in reverteds:
                if candidate in candidates:
                    self_revert = reverting["user"] == candidate["user"]

                    if not self_revert:
                        dataset.append((candidate["revid"], False))

    return dataset


