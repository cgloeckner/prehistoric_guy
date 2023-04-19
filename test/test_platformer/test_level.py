import unittest
import tempfile

from core import constants
from platformer import physics, level


class LevelTest(unittest.TestCase):

    def test__to_xml_from_xml_invert_each_other(self):
        scene = level.Scene(ctx=physics.Context())
        scene.ctx.create_platform(x=6.5, y=4.0, width=10, height=2)
        scene.ctx.create_platform(x=3.5, y=0.0, width=7)
        scene.ctx.create_ladder(x=3.25, y=0.5, height=4)
        scene.ctx.create_object(x=3.5, y=5.5, object_type=constants.ObjectType.FOOD)

        root = scene.to_xml()
        other = level.Scene.from_xml(root)

        self.assertEqual(len(other.ctx.platforms), 2)
        self.assertEqual(other.ctx.platforms[0].pos.x, 6.5)
        self.assertEqual(other.ctx.platforms[0].pos.y, 4.0)
        self.assertEqual(other.ctx.platforms[0].width, 10)
        self.assertEqual(other.ctx.platforms[0].height, 2)
        self.assertEqual(other.ctx.platforms[1].pos.x, 3.5)
        self.assertEqual(other.ctx.platforms[1].pos.y, 0.0)
        self.assertEqual(other.ctx.platforms[1].width, 7)
        self.assertEqual(len(other.ctx.ladders), 1)
        self.assertEqual(other.ctx.ladders[0].pos.x, 3.25)
        self.assertEqual(other.ctx.ladders[0].pos.y, 0.5)
        self.assertEqual(other.ctx.ladders[0].height, 4)
        self.assertEqual(len(other.ctx.objects), 1)
        self.assertEqual(other.ctx.objects[0].pos.x, 3.5)
        self.assertEqual(other.ctx.objects[0].pos.y, 5.5)
        self.assertEqual(other.ctx.objects[0].object_type, constants.ObjectType.FOOD)

    def test__to_file_from_file_invert_each_other(self):
        scene = level.Scene(ctx=physics.Context())
        scene.ctx.create_platform(x=6.5, y=4.0, width=10, height=2)
        scene.ctx.create_platform(x=3.5, y=0.0, width=7)
        scene.ctx.create_ladder(x=3.25, y=0.5, height=4)
        scene.ctx.create_object(x=3.5, y=5.5, object_type=constants.ObjectType.FOOD)

        with tempfile.NamedTemporaryFile('w') as file:
            scene.to_file(file.name)
            other = level.Scene.from_file(file.name)

        self.assertEqual(len(other.ctx.platforms), 2)
        self.assertEqual(other.ctx.platforms[0].pos.x, 6.5)
        self.assertEqual(other.ctx.platforms[0].pos.y, 4.0)
        self.assertEqual(other.ctx.platforms[0].width, 10)
        self.assertEqual(other.ctx.platforms[0].height, 2)
        self.assertEqual(other.ctx.platforms[1].pos.x, 3.5)
        self.assertEqual(other.ctx.platforms[1].pos.y, 0.0)
        self.assertEqual(other.ctx.platforms[1].width, 7)
        self.assertEqual(len(other.ctx.ladders), 1)
        self.assertEqual(other.ctx.ladders[0].pos.x, 3.25)
        self.assertEqual(other.ctx.ladders[0].pos.y, 0.5)
        self.assertEqual(other.ctx.ladders[0].height, 4)
        self.assertEqual(len(other.ctx.objects), 1)
        self.assertEqual(other.ctx.objects[0].pos.x, 3.5)
        self.assertEqual(other.ctx.objects[0].pos.y, 5.5)
        self.assertEqual(other.ctx.objects[0].object_type, constants.ObjectType.FOOD)
