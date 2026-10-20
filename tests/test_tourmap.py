import unittest

from sw import tourmap
from sw.ontology import Transition

STYLE = ("Helvetica", "#222222", "#888888", "#ffffff")


class TourMapTest(unittest.TestCase):
    def test_neighbours_apart(self):
        hues = [tourmap.colour(k) for k in range(6)]
        self.assertEqual(len(set(hues)), 6)

    def test_cross_arrows(self):
        ts = [Transition("leads_to", ("a",), ("b",)), Transition("calls", ("a", 1, 9), ("b", 0, 3)),
              Transition("calls", ("a", 0, 2), ("a", 1, 5)), Transition("own_trip", ("a", 0, 1), ("b",)),
              Transition("leads_to", ("a",), ("z",))]
        self.assertEqual(tourmap.cross_arrows(ts, ["a", "b"]),
                         [((0, 0), (1, 0), "leads_to"), ((0, 1), (1, 0), "calls")])

    def test_dot(self):
        source = tourmap.tour_dot([("A", [("x.py:f", 10), ("x.py:g", 30)]), ("B", [("y.py:h", 5)])],
                                  [((0, 1), (1, 0), "leads_to")], STYLE)
        self.assertIn('"1. A"', source)
        self.assertIn('"t0_s0" -> "t1_s0" [style=invis', source)
        self.assertIn('"t0_s1" -> "t1_s0" [penwidth=2.5, constraint=false]', source)

    def test_bands(self):
        got = tourmap.bands((0, 0, 100, 200), {0: (5, 150, 95, 195), 1: (5, 10, 95, 100)})
        self.assertEqual(got, [(0, 200, 125.0), (1, 125.0, 0)])
