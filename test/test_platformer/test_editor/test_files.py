import unittest
import tempfile
import pathlib

from core import constants
from platformer import physics
from platformer.editor import files


class LevelTest(unittest.TestCase):

    def test__to_xml_from_xml_invert_each_other(self):
        ctx = physics.Context()
        ctx.create_platform(x=6.5, y=4.0, width=10, height=2)
        ctx.create_platform(x=3.5, y=0.0, width=7)
        ctx.create_ladder(x=3.25, y=0.5, height=4)
        ctx.create_object(x=3.5, y=5.5, object_type=constants.ObjectType.FOOD)

        root = files.to_xml(ctx)
        other = files.from_xml(root)

        self.assertEqual(len(other.platforms), 2)
        self.assertEqual(other.platforms[0].pos.x, 6.5)
        self.assertEqual(other.platforms[0].pos.y, 4.0)
        self.assertEqual(other.platforms[0].width, 10)
        self.assertEqual(other.platforms[0].height, 2)
        self.assertEqual(other.platforms[1].pos.x, 3.5)
        self.assertEqual(other.platforms[1].pos.y, 0.0)
        self.assertEqual(other.platforms[1].width, 7)
        self.assertEqual(len(other.ladders), 1)
        self.assertEqual(other.ladders[0].pos.x, 3.25)
        self.assertEqual(other.ladders[0].pos.y, 0.5)
        self.assertEqual(other.ladders[0].height, 4)
        self.assertEqual(len(other.objects), 1)
        self.assertEqual(other.objects[0].pos.x, 3.5)
        self.assertEqual(other.objects[0].pos.y, 5.5)
        self.assertEqual(other.objects[0].object_type, constants.ObjectType.FOOD)

    def test__to_file_from_file_invert_each_other(self):
        ctx = physics.Context()
        ctx.create_platform(x=6.5, y=4.0, width=10, height=2)
        ctx.create_platform(x=3.5, y=0.0, width=7)
        ctx.create_ladder(x=3.25, y=0.5, height=4)
        ctx.create_object(x=3.5, y=5.5, object_type=constants.ObjectType.FOOD)

        root = files.to_xml(ctx)
        with tempfile.NamedTemporaryFile('w') as file:
            files.to_file(root, pathlib.Path(file.name))
            other = files.from_file(pathlib.Path(file.name))

        other = files.from_xml(other)

        self.assertEqual(len(other.platforms), 2)
        self.assertEqual(other.platforms[0].pos.x, 6.5)
        self.assertEqual(other.platforms[0].pos.y, 4.0)
        self.assertEqual(other.platforms[0].width, 10)
        self.assertEqual(other.platforms[0].height, 2)
        self.assertEqual(other.platforms[1].pos.x, 3.5)
        self.assertEqual(other.platforms[1].pos.y, 0.0)
        self.assertEqual(other.platforms[1].width, 7)
        self.assertEqual(len(other.ladders), 1)
        self.assertEqual(other.ladders[0].pos.x, 3.25)
        self.assertEqual(other.ladders[0].pos.y, 0.5)
        self.assertEqual(other.ladders[0].height, 4)
        self.assertEqual(len(other.objects), 1)
        self.assertEqual(other.objects[0].pos.x, 3.5)
        self.assertEqual(other.objects[0].pos.y, 5.5)
        self.assertEqual(other.objects[0].object_type, constants.ObjectType.FOOD)
