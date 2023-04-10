import unittest
import pygame

from core import resources

from platformer import render


class RenderSystemTest(unittest.TestCase):

    def setUp(self):
        surface = pygame.Surface((160, 120))
        cache = resources.Cache()

        # NOTE: due to limited test coverage for this class, the system arguments can be set to None safely
        self.sys = render.Renderer(None, None, cache, surface)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: regular coordinates
    def test__world_to_screen_coord__1(self):
        pos = self.sys.world_to_screen_coord(2.5, 3.5)
        self.assertEqual(pos.x, 2.5 * 32)
        self.assertEqual(pos.y, 120 - 3.5 * 32)

    # Case 2: using camera
    def test__world_to_screen_coord__2(self):
        self.sys.move_camera(5, 3)
        pos = self.sys.world_to_screen_coord(2.5, 3.5)
        self.assertEqual(pos.x, 2.5 * 32 - 5)
        self.assertEqual(pos.y, 120 - (3.5 * 32 - 3))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: regular coordinates
    def test__screen_to_world_coord__1(self):
        pos = self.sys.screen_to_world_coord(154, 97)
        self.assertAlmostEqual(pos.x, 154.0 / 32)
        self.assertAlmostEqual(pos.y, (120 - 97.0) / 32)

    # Case 2:
    def test__screen_to_world_coord__2(self):
        self.sys.move_camera(5, 3)
        pos = self.sys.screen_to_world_coord(154, 97)
        self.assertAlmostEqual(pos.x, 154.0 / 32 + 5)
        self.assertAlmostEqual(pos.y, (120 - 97.0) / 32 + 3)
