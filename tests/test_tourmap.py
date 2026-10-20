import unittest

from sw import tourmap
from sw.ontology import Transition

STYLE = ("Helvetica", "#222222", "#888888", "#ffffff")


class TourMapTest(unittest.TestCase):
    def test_cross_arrows(self):
        ts = [Transition("leads_to", ("a",), ("b",)), Transition("unblocks", ("a", 1, 9), ("b", 0, 3)),
              Transition("calls", ("a", 0, 2), ("b", 1, 5)), Transition("leads_to", ("a",), ("z",))]
        self.assertEqual(tourmap.cross_arrows(ts, ["a", "b"], [3, 2]),
                         [((0, 1), (1, 0), "unblocks"), ((0, 2), (1, 0), "leads_to")])

    def test_dot(self):
        source = tourmap.tour_dot([("A", [("x.py:f", 10, "#ffeedd"), ("x.py:g", 30, "#ffeedd")]),
                                   ("B", [("y.py:h", 5, "#ddeeff")])],
                                  [((0, 1), (1, 0), "leads_to")], STYLE)
        self.assertIn('"1. A"', source)
        self.assertIn('"t0_s0" -> "t0_s1" [style=invis', source)
        self.assertIn('"t0_s1" -> "t1_s0" [penwidth=2.5];', source)
        self.assertIn('"cluster_legend"', source)

    def test_tiles(self):
        rows = tourmap.tiles((0, 0, 100, 100), {0: (0, 50, 50, 100)}, 100, 100, 25)
        self.assertEqual(rows[0], (0, 25, [(0, 50, 0), (50, 100, None)]))
        self.assertEqual(rows[3], (75, 100, [(0, 100, None)]))
