import unittest
import os
import pygame

from core import constants

from platformer.renderer import base, shapes
from platformer import physics


class ShapeRendererTest(unittest.TestCase):

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

        self.cam = base.Camera(320, 192)
        self.cam.topleft.x = -1.5
        self.cam.topleft.y = -0.5

        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        self.buffer = pygame.Surface((self.cam.width, self.cam.height))

        self.renderer = shapes.ShapeRenderer(self.cam, self.buffer, self.ctx)

    # ------------------------------------------------------------------------------------------------------------------

    def test__from_world_coord(self):
        w_pos = pygame.math.Vector2(2.5, 3.5)
        s_pos = self.renderer.from_world_coord(w_pos)

        self.assertAlmostEqual(s_pos.x, (2.5 + 1.5) * constants.WORLD_SCALE)
        self.assertAlmostEqual(s_pos.y, self.cam.height - (3.5 + 0.5) * constants.WORLD_SCALE)

        # coord inversion
        pos = self.renderer.to_world_coord(s_pos)
        self.assertAlmostEqual(pos.x, w_pos.x)
        self.assertAlmostEqual(pos.y, w_pos.y)

    def test__to_world_coord(self):
        s_pos = pygame.math.Vector2(154, 97)
        w_pos = self.renderer.to_world_coord(s_pos)

        self.assertAlmostEqual(w_pos.x, 154.0 / constants.WORLD_SCALE - 1.5)
        self.assertAlmostEqual(w_pos.y, (self.cam.height - 97.0) / constants.WORLD_SCALE - 0.5)

        # coord inversion
        pos = self.renderer.from_world_coord(w_pos)
        self.assertAlmostEqual(pos.x, s_pos.x)
        self.assertAlmostEqual(pos.y, s_pos.y)

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_platform_rect(self):
        platform = self.ctx.platforms[0]
        pos = self.renderer.get_platform_rect(platform)

        self.assertEqual(pos.left, (1 + 1.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.top, 192 - (0 + 0.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.width, 3 * constants.WORLD_SCALE)
        self.assertEqual(pos.height, 2 * constants.WORLD_SCALE)

    def test__get_ladder_rect(self):
        ladder = self.ctx.ladders[0]
        pos = self.renderer.get_ladder_rect(ladder)

        self.assertEqual(pos.centerx, (9 + 1.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.bottom, 192 - (3 + 0.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.width, constants.WORLD_SCALE)
        self.assertEqual(pos.height, 2 * constants.WORLD_SCALE)

    def test__get_object_rect(self):
        obj = self.ctx.objects[0]
        pos = self.renderer.get_object_rect(obj)

        self.assertEqual(pos.centerx, (1.5 + 1.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.bottom, 192 - (3 + 0.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.width, constants.OBJECT_SCALE)
        self.assertEqual(pos.height, constants.OBJECT_SCALE)

    def test__get_actor_rect(self):
        actor = self.ctx.actors[0]
        pos = self.renderer.get_actor_rect(actor)

        self.assertEqual(pos.centerx, (8.5 + 1.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.bottom, 192 - (5 + 0.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.width, constants.SPRITE_SCALE)
        self.assertEqual(pos.height, constants.SPRITE_SCALE)

    def test__get_projectile_rect(self):
        proj = self.ctx.projectiles[0]
        pos = self.renderer.get_projectile_rect(proj)

        self.assertEqual(pos.centerx, (6.5 + 1.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.centery, 192 - (5.5 + 0.5) * constants.WORLD_SCALE)
        self.assertEqual(pos.width, constants.OBJECT_SCALE)
        self.assertEqual(pos.height, constants.OBJECT_SCALE)

    # ------------------------------------------------------------------------------------------------------------------

    def test_draw_does_not_raise(self):
        self.renderer.draw()
