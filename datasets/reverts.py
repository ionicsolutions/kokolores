import mwapi
import mwreverts

from itertools import islice

my_agent = 'kokolores dataset creator <kilian.kluge@wikipedia.de>'
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
                               revids=batch_ids, rvprops='ids|content')

            for page_doc in doc['query']['pages']:
                page_meta = {k: v for k, v in page_doc.items()
                             if k != 'revisions'}
                if 'revisions' in page_doc:
                    for revision_doc in page_doc['revisions']:
                        yield (revision_doc['content'], {"rev_id" : revision_doc['revid']})

def get_reverted_revisions(revids):
    return [revision for revision in get_content_by_revids(revids)]
