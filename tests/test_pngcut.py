import os
import tempfile
import unittest

from sw import pngcut


class PngCutTest(unittest.TestCase):
    def test_round_trip_and_crop(self):
        rows = [b"".join(bytes([x, y, 7, 255]) for x in range(4)) for y in range(3)]
        path = os.path.join(tempfile.mkdtemp(), "a.png")
        pngcut.write(path, 4, 3, 6, rows)
        self.assertEqual(pngcut.read(path), (4, 3, 6, rows))
        self.assertEqual(pngcut.crop(rows, 6, 1, 1, 3, 2), [rows[1][4:12]])
