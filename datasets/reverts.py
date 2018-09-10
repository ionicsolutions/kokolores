import mwapi
import mwreverts
import logging

from itertools import islice
logging.basicConfig(level=logging.DEBUG)


class RevertDetector:

    def __init__(self, db):
        self.logger = logging.getLogger("kokolores.reverts")
        my_agent = "kokolores dataset creator " \
                   "<kokolores.datasets@tools.wmflabs.org>"
        self.session = mwapi.Session("https://%s.wikipedia.org" % db[:2],
                                     formatversion=2,
                                     user_agent=my_agent)
        self.logger.debug("Initialized session.")

    # based on https://github.com/mediawiki-utilities/python-mwapi/blob/master/demo_queries.py
    def get_content_by_revids(self, revids, batch=50):
        revids_iter = iter(revids)
        while True:
            batch_ids = list(islice(revids_iter, 0, batch))
            if len(batch_ids) == 0:
                break
            else:
                doc = self.session.post(action='query',
                                        prop='revisions',
                                        revids=batch_ids,
                                        rvprop='ids|sha1|user')

                for page_doc in doc['query']['pages']:
                    if 'revisions' in page_doc:
                        for revision_doc in page_doc['revisions']:
                            try:
                                yield (revision_doc['sha1'],
                                       {"rev_id": revision_doc['revid'],
                                        "user": revision_doc["user"]})
                            except KeyError:
                                continue

    def get_all(self, all_revisions, candidates, all_approved):
        """Find all reverts of unapproved revisions back to the latest approved
        revision.

        Based on the example given in https://github.com/wiki-ai/editquality/blob/master/ipython/reverted_detection_demo.ipynb
        but adapted significantly to the problem context.

        :param all_revisions: List of all revision IDs.
        :param candidates: List of all unapproved revision IDs.
        :param all_approved: List of all approved revision IDs.
        :return:
        """
        revisions = list(self.get_content_by_revids(all_revisions))

        dataset = []
        revert_destination = []
        for reverting, reverteds, reverted_to in mwreverts.detect(revisions,
                                                                  radius=5):
            # ignore reverts with unknown target
            if reverted_to is None:
                print("No target for %d" % reverting["rev_id"])
                continue
            else:
                revert_destination.append(reverted_to["rev_id"])

            # ignore reverts which were not approved
            if reverting["rev_id"] not in all_approved:
                print("Revert %d was not approved." % reverting["rev_id"])
                continue

            # ignore reverts whose target is not approved
            if reverted_to["rev_id"] not in all_approved:
                print("Revert %d has unnaproved targed %d"
                      % (reverting["rev_id"], reverted_to["rev_id"]))
                continue

            if reverteds is not None:
                # the revision we are interested in is the latest unapproved
                # revision prior to the revert, i.e. what the reverting user
                # saw when making their decision
                candidate = max(reverteds, key=lambda item: item["rev_id"])
                print("Candidate %s out of %s" % (candidate, reverteds))

                # filter out reverts whose target is not the latest approved
                # revision (that's beyond the scope of kokolores)
                latest_approved = max([rev_id for rev_id in all_approved
                                       if rev_id < candidate["rev_id"]])
                print("Latest approved revision is %d" % latest_approved)

                if (latest_approved == reverted_to["rev_id"]):
                    if candidate["rev_id"] in candidates:
                        self_revert = candidate["user"] == reverted_to["user"]
                        if not self_revert:
                            dataset.append((candidate["rev_id"],
                                            False,
                                            reverted_to["rev_id"]))
                        else:
                            print("Self revert!")
                    else:
                        print("Candidate is in flaggedrevs table")
                else:
                    print("Target is not latest")

        return [item for item in dataset if item[0] not in revert_destination]
