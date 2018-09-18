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
import time

from reverts import RevertDetector
from utils import load_query


# Load SQL query for all manually approved revisions
# based on https://quarry.wmflabs.org/query/27156
MANUALLY_APPROVED = load_query("queries/manually_approved.sql")

# Load SQL query for potentially reverted revisions
# based on https://quarry.wmflabs.org/query/27161
POTENTIALLY_REVERTED = load_query("queries/potentially_reverted.sql")

# Load SQL query for all revisions of a page
# based on https://quarry.wmflabs.org/query/27173
ALL_REVISIONS = load_query("queries/all_revisions.sql")

# Load SQL query to fetch all approved revisions of a page
ALL_APPROVED = load_query("queries/all_approved.sql")

# Load SQL query for a randomized batch of pages with flagged revision data
RANDOM_BATCH = load_query("queries/random_batch.sql")

# Load SQL query to fetch all pages with flagged revision data within
# a certain period of time
TIMEFRAME_BATCH = load_query("queries/timeframe_batch.sql")


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
    START_DEFAULT = 20080507000000  # FlaggedRevs started on May 6th 2008
    STOP_DEFAULT = int(time.strftime("%Y%m%d%H%M%S", time.gmtime())) + 1000000

    def __init__(self, db="dewiki_p", revert_detector=None):
        self.logger = logging.getLogger("kokolores.creator")

        self.start = self.START_DEFAULT
        self.stop = self.START_DEFAULT

        if revert_detector is None:
            self.revert_detector = RevertDetector(db)
        else:
            self.revert_detector = revert_detector
        self.conn = toolforge.connect(db,
                                      cursorclass=pymysql.cursors.DictCursor)

    def create(self, size=None, start=None, stop=None, batch_size=1000,
               fname=None, resume=True, keep_tmp=True):
        """Generate a new dataset.

        :param size: Total size of the data set.
        :param start: Start of the time period.
        :param stop: End of the time period.
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
        if start is None:
            self.start = self.START_DEFAULT
        else:
            self.start = start

        if stop is None:
            self.stop = self.START_DEFAULT
        else:
            self.stop = stop

        if self.start > self.stop:
            raise ValueError("Start (%d) has to come before stop (%d)"
                             % (self.start, self.stop))

        if fname is not None and os.path.exists("%s.tmp" % fname) \
                and os.path.exists("%s.pages.tmp" % fname) and resume:
            dataset = self._load("%s.tmp" % fname)
            pages = self._load("%s.pages.tmp" % fname)
        else:
            dataset = []
            pages = []

        if size is None:
            get_batch = self._get_timeframe_batch
        else:
            get_batch = self._get_random_batch

        for batch in get_batch(batch_size):
            self.logger.info("Processing batch of %d pages", len(batch))
            batch = [page_id for page_id in batch
                     if page_id not in pages]
            pages.extend(batch)

            for page_id in batch:
                dataset.extend(self._find_approved(page_id))
                dataset.extend(self._find_reverted(page_id))

            self.logger.info("Dataset has %d entries now.", len(dataset))

            if size is not None:
                if len(dataset) >= size:
                    dataset = dataset[:size]
                    break

            if fname is not None:
                self._store("%s.tmp" % fname, dataset)
                self._store("%s.pages.tmp" % fname, pages)

        if fname is not None:
            self._store(fname, dataset)
            if not keep_tmp:
                os.remove("%s.tmp" % fname)
                os.remove("%s.pages.tmp" % fname)
        return dataset

    def _store(self, fname, data):
        self.logger.info("Writing data to file %s", fname)
        with bz2.open(fname, "wt") as f:
            json.dump(data, f)

    def _load(self, fname):
        self.logger.info("Loading data from file %s", fname)
        with bz2.open(fname, "rt") as f:
            return json.load(f)

    def _get_random_batch(self, size=1000):
        self.logger.info("Get random batch of size %d", size)
        while True:
            with self.conn.cursor() as cursor:
                cursor.execute(RANDOM_BATCH, {"num": size})
                self.conn.commit()
                batch = [int(item["page_id"]) for item in cursor.fetchall()]
            self.logger.info("Prepared batch of %d pages", len(batch))
            yield batch

    def _get_timeframe_batch(self, size=1000):
        self.logger.info("Get all pages in timeframe %d to %d",
                         self.start, self.stop)
        with self.conn.cursor() as cursor:
            cursor.execute(TIMEFRAME_BATCH, {"start": self.start,
                                             "stop": self.stop})
            self.conn.commit()
            batch = [int(item["page_id"]) for item in cursor.fetchall()]
        self.logger.info("Prepared timeframe batch of %d pages", len(batch))
        for i in range(0, len(batch), size):
            yield batch[i:i + size]

    def _find_approved(self, page_id):
        """Find all manually approved revisions of a page."""
        with self.conn.cursor() as cursor:
            cursor.execute(MANUALLY_APPROVED, {"page_id": page_id,
                                               "start": self.start,
                                               "stop": self.stop})
            self.conn.commit()
            for item in cursor.fetchall():
                yield (item["rev_id"], True, item["rev_parent"])

    def _find_reverted(self, page_id):
        with self.conn.cursor() as cursor:
            # Find all revisions which were neither auto-approved
            # nor manually approved
            cursor.execute(POTENTIALLY_REVERTED, {"page_id": page_id,
                                                  "start": self.start,
                                                  "stop": self.stop})
            self.conn.commit()
            result = cursor.fetchall()
            candidates = [item["rev_id"] for item in result]

            if not candidates:
                return []

            # Retrieve all revisions of the page for revert detection
            cursor.execute(ALL_REVISIONS, {"page_id": page_id,
                                           "from_rev": min(candidates),
                                           "start": self.start,
                                           "stop": self.stop})
            self.conn.commit()
            result = cursor.fetchall()
            all_revisions = [item["rev_id"] for item in result]

            # Retrieve all approved revisions of the page
            cursor.execute(ALL_APPROVED, {"page_id": page_id,
                                               "from_rev": min(candidates),
                                               "start": self.start,
                                               "stop": self.stop})
            self.conn.commit()
            result = cursor.fetchall()
            all_approved_revisions = [item["rev_id"] for item in result]

        return self.revert_detector.get_all(all_revisions, candidates,
                                            all_approved_revisions)

    def __del__(self):
        self.logger.info("Closing database connection")
        self.conn.close()
