from utils import load_query
import unittest
import toolforge
import pymysql


class TestAllRevisions(unittest.TestCase):

    def setUp(self):
        self.FETCH_ALL_REVISIONS = load_query("queries/all_revisions.sql")

        self.conn = toolforge.connect("dewiki_p",
                                      cursorclass=pymysql.cursors.DictCursor)

    def test_all_revisions(self):
        revisions = [
            116390597,
            116390642,
            116390700,
            116392568,
            137273510,
            137305128,
            148741571,
            177861065
        ]

        with self.conn.cursor() as cursor:
            cursor.execute(self.FETCH_ALL_REVISIONS, {"page_id": 7615875,
                                                      "from_rev": 0,
                                                      "start": 20130330000000,
                                                      "stop": 20180531000000})
            self.conn.commit()
            result = cursor.fetchall()
            all_revisions = [item["rev_id"] for item in result]

        self.assertEqual(revisions, all_revisions)

    def test_timeframe(self):

        revisions_2013 = [
            116390597,
            116390642,
            116390700,
            116392568
        ]

        with self.conn.cursor() as cursor:
            cursor.execute(self.FETCH_ALL_REVISIONS, {"page_id": 7615875,
                                                      "from_rev": 0,
                                                      "start": 20130101000000,
                                                      "stop": 20140101000000})
            self.conn.commit()
            result = cursor.fetchall()
            all_revisions = [item["rev_id"] for item in result]

        self.assertEqual(revisions_2013, all_revisions)
