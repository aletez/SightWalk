import unittest

from sw.history import History


class HistoryTest(unittest.TestCase):
    def test_back_and_forward(self):
        h = History()
        h.visit("a", None)
        h.visit("b", None, "U: q\n\n")
        h.keep("talk in b", {"answers": []})
        self.assertFalse(h.can(1))
        self.assertEqual(h.go(-1)["trip"], "a")
        self.assertIsNone(h.go(-1))
        entry = h.go(1)
        self.assertEqual((entry["trip"], entry["transcript"]), ("b", "talk in b"))

    def test_visit_drops_the_trips_ahead(self):
        h = History()
        for trip in "abc":
            h.visit(trip, None)
        h.go(-1)
        h.go(-1)
        h.visit("d", None)
        self.assertEqual([e["trip"] for e in h.entries], ["a", "d"])
        self.assertFalse(h.can(1))
