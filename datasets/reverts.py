import mwapi
import mwreverts

from itertools import islice


class RevertDetector:

    def __init__(self, db):
        my_agent = "kokolores dataset creator "\
                   "<kokolores.datasets@tools.wmflabs.org>"
        self.session = mwapi.Session("https://%s.wikipedia.org" % db[:2],
                                formatversion=2,
                                user_agent=my_agent)

    # based on https://github.com/mediawiki-utilities/python-mwapi/blob/master/demo_queries.py
    def get_content_by_revids(self, revids, batch=50):
        revids_iter = iter(revids)
        while True:
            batch_ids = list(islice(revids_iter, 0, batch))
            if len(batch_ids) == 0:
                break
            else:
                doc = self.session.post(action='query', prop='revisions',
                                   revids=batch_ids, rvprop='ids|sha1|user')

                for page_doc in doc['query']['pages']:
                    if 'revisions' in page_doc:
                        for revision_doc in page_doc['revisions']:
                            try:
                                yield (revision_doc['sha1'],
                                       {"rev_id" : revision_doc['revid'],
                                        "rev_parent": revision_doc['parentid'],
                                        "user" : revision_doc["user"]})
                            except KeyError:
                                continue

    # based on https://github.com/wiki-ai/editquality/blob/master/ipython/reverted_detection_demo.ipynb
    def get_all(self, revids, candidates):
        revisions = list(self.get_content_by_revids(revids))

        dataset = []
        revert_destination = []
        for reverting, reverteds, reverted_to in mwreverts.detect(revisions,
                                                                  radius=5):
            if reverted_to is not None:
                revert_destination.append(reverted_to)

            if reverteds is not None:
                for candidate in reverteds:
                    if candidate["rev_id"] in candidates:
                        self_revert = reverting["user"] == candidate["user"]

                        if not self_revert:
                            dataset.append((candidate["rev_id"],
                                            False,
                                            candidate["rev_parent"]))

        return [item for item in dataset if item[0] not in revert_destination]


