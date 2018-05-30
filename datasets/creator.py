# MIT License
#
# Copyright (c) 2018 Kilian Kluge
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging
import pymysql
import toolforge
import json
import bz2
import os

from reverts import RevertDetector

# Load SQL query for all manually approved revisions
# based on https://quarry.wmflabs.org/query/27156
with open("queries/manually_reviewed.sql", "r") as queryfile:
    MANUALLY_REVIEWED = queryfile.read()

# Load SQL query for potentially reverted revisions
# based on https://quarry.wmflabs.org/query/27161
with open("queries/potentially_reverted.sql", "r") as queryfile:
    POTENTIALLY_REVERTED = queryfile.read()

# Load SQL query for all revisions of a page
# based on https://quarry.wmflabs.org/query/27173
with open("queries/all_revisions.sql", "r") as queryfile:
    FETCH_ALL_REVISIONS = queryfile.read()

# Load SQL query for a randomized batch of pages with flagged revision data
with open("queries/random_batch.sql", "r") as queryfile:
    RANDOM_BATCH = queryfile.read()


class Creator:
    """Creator for Flagged Revision datasets.

       Each dataset entry is a 3-tuple `(int, bool, int)` where the
       first entry is the `rev_id` of the revision in question,
       the second entry indicates whether the revision was manually
       approved or rejected, and the third entry is the `rev_id` of
       the preceding approved revision. The latter was approved
       either manually or automatically.

       Dataset creation will work for all wikis where a substantial
       amount of revisions have been reviewed through the FlaggedRevs
       extension.

       """
    ROW_LIMIT = 1000  # Maximum number of rows to retrieve per flaggedrevs query

    def __init__(self, db="dewiki_p", revert_detector=None):
        self.logger = logging.getLogger("kokolores.creator")
        if revert_detector is None:
            self.revert_detector = RevertDetector(db)
        else:
            self.revert_detector = revert_detector
        self.conn = toolforge.connect(db,
                                      cursorclass=pymysql.cursors.DictCursor)

    def create(self, size, batch_size=1000,
               fname=None, resume=True, keep_tmp=False):
        """Generate a new dataset.

        :param size: Total size of the data set.
        :param batch_size: Number of pages to retrieve data for at once.
        :param fname: If given, store the dataset in this file (bzipped JSON)
                      and store a temporary copy after each batch. Useful for
                      large datasets.
        :param resume: If `True`, look for temporary files and resume dataset
                       creation.
        :param keep_tmp: If `True`, do not delete temporary files after
                         dataset creation is completed.
        :type size: int
        :type batch_size: int
        :type fname: str
        :type resume: bool
        :type keep_tmp: bool
        :return: A dataset with `size` entries.
        """
        if fname is not None and os.path.exists("%s.tmp" % fname) \
                and os.path.exists("%s.pages.tmp" % fname) and resume:
            dataset = self._load("%s.tmp" % fname)
            pages = self._load("%s.pages.tmp" % fname)
        else:
            dataset = []
            pages = []

        while len(dataset) < size:
            batch = [page_id for page_id in self._get_batch(batch_size)
                     if page_id not in pages]
            pages.extend(batch)
            for page_id in batch:
                dataset.extend(self._find_approved(page_id))
                dataset.extend(self._find_reverted(page_id))

            if fname is not None:
                self._store("%s.tmp" % fname, dataset)
                self._store("%s.pages.tmp" % fname, pages)

        dataset = dataset[:size]
        if fname is not None:
            self._store(fname, dataset)
            if not keep_tmp:
                os.remove("%s.tmp" % fname)
                os.remove("%s.pages.tmp" % fname)
        return dataset

    def _store(self, fname, data):
        with bz2.open(fname, "wt") as f:
            json.dump(data, f)

    def _load(self, fname):
        with bz2.open(fname, "rt") as f:
            return json.load(f)

    def _get_batch(self, size=1000):
        with self.conn.cursor() as cursor:
            cursor.execute(RANDOM_BATCH, {"num": size})
            self.conn.commit()
            batch = [int(item["page_id"]) for item in cursor.fetchall()]
        self.logger.info("Prepared batch of %d pages", len(batch))
        return batch

    def _find_approved(self, page_id):
        """Find all manually approved revisions"""
        with self.conn.cursor() as cursor:
            cursor.execute(MANUALLY_REVIEWED, {"page_id": page_id,
                                               "row_limit": self.ROW_LIMIT})
            self.conn.commit()
            for item in cursor.fetchall():
                yield (item["rev_id"], True, item["rev_parent"])

    def _find_reverted(self, page_id):
        with self.conn.cursor() as cursor:
            # Find all revisions which were neither auto-approved
            # nor manually approved
            cursor.execute(POTENTIALLY_REVERTED, {"page_id": page_id,
                                                  "row_limit": self.ROW_LIMIT})
            self.conn.commit()
            result = cursor.fetchall()
            candidates = [item["rev_id"] for item in result]

            if not candidates:
                return []

            # Retrieve all revisions of the page for revert detection
            cursor.execute(FETCH_ALL_REVISIONS, {"page_id": page_id,
                                                 "from_rev": min(candidates)})
            self.conn.commit()
            result = cursor.fetchall()
            all_revisions = [item["rev_id"] for item in result]

        return self.revert_detector.get_all(all_revisions, candidates)

    def __del__(self):
        self.conn.close()
