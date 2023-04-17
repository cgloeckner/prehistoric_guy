import unittest

from core import constants
from platformer.renderer import base, ascii
from platformer import physics


class AsciiRendererTest(unittest.TestCase):

    def setUp(self):
        self.ctx = physics.Context()
        self.ctx.create_platform(x=1, y=0, width=3, height=2)
        self.ctx.create_platform(x=8, y=3, width=4)
        self.ctx.create_platform(x=7, y=5, width=2)
        self.ctx.create_platform(x=1, y=5, width=3)
        self.ctx.create_ladder(x=9, y=3, height=2)
        self.ctx.create_object(x=1.5, y=3, object_type=constants.ObjectType.FOOD)
        self.ctx.create_actor(1, x=8.5, y=5)
        self.ctx.create_projectile(2, x=6.5, y=5.5)

        self.cam = base.Camera(10, 6)
        self.cam.center.x = -1.0

        self.renderer = ascii.AsciiRenderer(self.cam, self.ctx)

    def test_buffer_output(self):
        self.renderer.draw()

        # test buffer
        self.assertEqual(len(self.renderer.buffer), 6)
        self.assertEqual(''.join(self.renderer.buffer[0]), '.___...__.')
        self.assertEqual(''.join(self.renderer.buffer[1]), '......*.A#')
        self.assertEqual(''.join(self.renderer.buffer[2]), '........_#')
        self.assertEqual(''.join(self.renderer.buffer[3]), '.o__......')
        self.assertEqual(''.join(self.renderer.buffer[4]), '.XXX......')
        self.assertEqual(''.join(self.renderer.buffer[5]), '.XXX......')
