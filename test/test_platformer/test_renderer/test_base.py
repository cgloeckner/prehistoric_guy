import unittest
import pygame

from platformer.renderer import base


class CameraTest(unittest.TestCase):

    def test__set_center(self):
        scale = 10
        cam = base.Camera(320, 200)  # 32 x 20
        w_pos = pygame.math.Vector2(1.5, 0.75)
        cam.set_center(w_pos, scale)
        self.assertEqual(cam.topleft.x, 1.5 - 16)
        self.assertEqual(cam.topleft.y, 0.75 - 10)

    def test__from_world_coord(self):
        cam = base.Camera(320, 200)
        cam.topleft.x = 1.5
        cam.topleft.y = -0.75
        w_pos = pygame.math.Vector2(7.5, 2.5)
        s_pos = cam.from_world_coord(w_pos)

        self.assertAlmostEqual(s_pos.x, 6)
        self.assertAlmostEqual(s_pos.y, 3.25)

        # coord inversion
        pos = cam.to_world_coord(s_pos)
        self.assertAlmostEqual(pos.x, w_pos.x)
        self.assertAlmostEqual(pos.y, w_pos.y)

    def test__screen_to_world_coord__1(self):
        cam = base.Camera(320, 200)
        cam.topleft.x = -7.2
        cam.topleft.y = -3.9
        s_pos = pygame.math.Vector2(4.5, 9.7)
        w_pos = cam.to_world_coord(s_pos)

        self.assertAlmostEqual(w_pos.x, -2.7)
        self.assertAlmostEqual(w_pos.y, 5.8)

        # coord inversion
        pos = cam.from_world_coord(w_pos)
        self.assertAlmostEqual(pos.x, s_pos.x)
        self.assertAlmostEqual(pos.y, s_pos.y)
