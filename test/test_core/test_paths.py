import unittest
import tempfile
import pathlib

from core import paths


class DataPathTest(unittest.TestCase):

    def test__levels(self):
        with tempfile.TemporaryDirectory() as tmpdir_name:
            path = pathlib.Path(tmpdir_name)
            d = paths.DataPath(path)

            # data/levels
            lvl_path = d.level()
            self.assertTrue(lvl_path.exists())
            self.assertTrue(lvl_path.is_dir())

            lvl_file = d.level('foo')
            self.assertEqual(lvl_file.suffix, '.xml')

            # data/language
            lang_path = d.language()
            self.assertTrue(lang_path.exists())
            self.assertTrue(lang_path.is_dir())

            lang_file = d.language('bar')
            self.assertEqual(lang_file.suffix, '.ini')

            # data/tiles
            tile_path = d.tile()
            self.assertTrue(tile_path.exists())
            self.assertTrue(tile_path.is_dir())

            tile_file = d.tile('ugly')
            self.assertEqual(tile_file.suffix, '.png')

            # data/sprites
            sprite_path = d.sprite()
            self.assertTrue(sprite_path.exists())
            self.assertTrue(sprite_path.is_dir())

            sprite_file = d.sprite('bob')
            self.assertEqual(sprite_file.suffix, '.png')
