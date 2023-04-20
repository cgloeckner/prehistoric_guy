import unittest
import tempfile
import pathlib

from core import paths


class DataPathTest(unittest.TestCase):

    def test__levels(self):
        with tempfile.TemporaryDirectory() as tmpdir_name:
            path = pathlib.Path(tmpdir_name)
            d = paths.DataPath(path)

            lvl_path = d.levels()
            self.assertEqual(path / 'levels', lvl_path)
            self.assertTrue(lvl_path.exists())
            self.assertTrue(lvl_path.is_dir())

            lvl_file = d.levels('foo')
            self.assertEqual(path / 'levels' / 'foo.xml', lvl_file)
            self.assertFalse(lvl_file.exists())
