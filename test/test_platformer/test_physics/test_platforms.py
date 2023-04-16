import unittest
import math
import pygame
from typing import List

from platformer.physics import platforms


class PlatformPhysicsTest(unittest.TestCase):

    # Case 1: no hovering functions yields no movement
    def test__get_hover_delta__1(self):
        hover = platforms.Hovering()
        delta = hover.get_hover_delta(25)

        self.assertEqual(hover.index, 1)
        self.assertAlmostEqual(delta.x, 0.0)
        self.assertAlmostEqual(delta.y, 0.0)

    # Case 2: hovering can be either or in both directions
    def test__get_hover_delta__2(self):
        hover = platforms.Hovering(x=math.sin)
        delta = hover.get_hover_delta(25)

        self.assertEqual(hover.index, 1)
        self.assertGreater(delta.x, 0.0)
        self.assertAlmostEqual(delta.y, 0.0)

        hover = platforms.Hovering(y=math.sin)
        delta = hover.get_hover_delta(25)

        self.assertEqual(hover.index, 1)
        self.assertAlmostEqual(delta.x, 0.0)
        self.assertGreater(delta.y, 0.0)

        hover = platforms.Hovering(x=math.cos, y=math.sin)
        delta = hover.get_hover_delta(25)

        self.assertEqual(hover.index, 1)
        self.assertGreater(delta.x, 0.0)
        self.assertGreater(delta.y, 0.0)

    # Case 3: hovering with zero amplitude yields no movement
    def test__get_hover_delta__3(self):
        hover = platforms.Hovering(x=math.sin, y=math.cos, amplitude=0.0)
        delta = hover.get_hover_delta(25)

        self.assertEqual(hover.index, 1)
        self.assertAlmostEqual(delta.x, 0.0)
        self.assertAlmostEqual(delta.y, 0.0)

    # ------------------------------------------------------------------------------------------------------------------

    def test__apply_hovering(self):
        hover = platforms.Hovering(x=math.sin, y=math.cos)
        platform = platforms.Platform(pygame.math.Vector2(3, 1), width=3)

        # no hovering yields no motion
        delta = platform.apply_hovering(10)
        self.assertAlmostEqual(delta.x, 0.0)
        self.assertAlmostEqual(delta.y, 0.0)

        # hovering yields some motion
        hover_copy = platforms.Hovering(x=math.sin, y=math.cos)
        platform.hover = hover
        delta = platform.apply_hovering(10)
        expected = hover_copy.get_hover_delta(10)
        self.assertAlmostEqual(delta.x, expected.x)
        self.assertAlmostEqual(delta.y, expected.y)
        self.assertAlmostEqual(platform.pos.x, 3 + delta.x)
        self.assertAlmostEqual(platform.pos.y, 1 + delta.y)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: position inside platform
    # NOTE: y is the top, so y - height leads to the bottom
    def test__contains_point__1(self):
        plat = platforms.Platform(pygame.math.Vector2(3, 2), 10, 5)
        self.assertTrue(plat.contains_point(pygame.math.Vector2(4, 3)))

    # Case 2: position at platform's top
    def test__contains_point__2(self):
        plat = platforms.Platform(pygame.math.Vector2(3, 2), 10, 5)

        # top edge does not count as inside
        self.assertFalse(plat.contains_point((pygame.math.Vector2(6, 7))))
                                             
        # left/right/bottom edges do
        self.assertTrue(plat.contains_point(pygame.math.Vector2(3, 2)))
        self.assertTrue(plat.contains_point(pygame.math.Vector2(13, 5)))
        self.assertTrue(plat.contains_point(pygame.math.Vector2(6, 2)))

    # Case 3: position outside platform
    def test__contains_point__3(self):
        plat = platforms.Platform(pygame.math.Vector2(3, 2), 10, 5)

        # above/below/left/right
        self.assertFalse(plat.contains_point(pygame.math.Vector2(4, 8)))
        self.assertFalse(plat.contains_point(pygame.math.Vector2(4, 1)))
        self.assertFalse(plat.contains_point(pygame.math.Vector2(1, 5)))
        self.assertFalse(plat.contains_point(pygame.math.Vector2(14, 5)))

    # Case 4: thin platform never contains a point
    def test__contains_point__4(self):
        plat = platforms.Platform(pygame.math.Vector2(3, 2), 10)
        self.assertFalse(plat.contains_point(pygame.math.Vector2(5, 2)))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: directly stands on platform
    def test__supports_point__1(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 3), width=3)
        self.assertTrue(plat.supports_point(pygame.math.Vector2(2, 3)))

        # higher platform (y_top == 4
        plat = platforms.Platform(pygame.math.Vector2(1, 3), width=3, height=1)
        self.assertFalse(plat.supports_point(pygame.math.Vector2(2, 3)))
        self.assertTrue(plat.supports_point(pygame.math.Vector2(2, 4)))

    # Case 2: is above platform
    def test__supports_point__2(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 3), width=3)
        self.assertFalse(plat.supports_point(pygame.math.Vector2(2, 3.1)))

    # Case 3: is below platform
    def test__supports_point__3(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 3), width=3)
        self.assertFalse(plat.supports_point(pygame.math.Vector2(2, 2.9)))

    # Case 4: is left of platform
    def test__supports_point__4(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 3), width=3)
        self.assertFalse(plat.supports_point(pygame.math.Vector2(0.9, 3)))

    # Case 5: is right of platform
    def test__supports_point__6(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 3), width=3)
        self.assertFalse(plat.supports_point(pygame.math.Vector2(4.1, 3)))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: traversing downwards
    def test__was_traverse_from_above__1(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 2), 10)
        self.assertTrue(plat.was_traverse_from_above(pygame.math.Vector2(2, 3), pygame.math.Vector2(3, -4)))

    # Case 2: no traversing upwards
    def test__was_traverse_from_above__2(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 2), 10)
        self.assertFalse(plat.was_traverse_from_above(pygame.math.Vector2(2, -3), pygame.math.Vector2(3, 4)))

    # Case 3: no traversing if last_pos == (x, y)
    def test__was_traverse_from_above__3(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 2), 10)
        self.assertFalse(plat.was_traverse_from_above(pygame.math.Vector2(2, 3), pygame.math.Vector2(2, 3)))

    # Case 4: traversing with last_pos on platform
    def test__was_traverse_from_above__4(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 2), 10)
        self.assertTrue(plat.was_traverse_from_above(pygame.math.Vector2(1, 2), pygame.math.Vector2(2, -3)))

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_landing_point(self):
        plat = platforms.Platform(pygame.math.Vector2(1, 2), 10)
        pos = plat.get_landing_point(pygame.math.Vector2(2, 3), pygame.math.Vector2(3, -4))
        self.assertAlmostEqual(pos.x, 2.143, places=2)
        self.assertAlmostEqual(pos.y, 2)

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_platform_collision(self):
        plats: List[platforms.Platform] = list()

        # no collision if no platforms
        p = platforms.get_platform_collision(pygame.math.Vector2(), plats)
        self.assertIsNone(p)

        # no collision if platforms are not relevant
        plats.append(platforms.Platform(pygame.math.Vector2(1, 2), 3, 1))  # does not contain (0, 0)
        p = platforms.get_platform_collision(pygame.math.Vector2(), plats)
        self.assertIsNone(p)

        # get first platform that fits collision condition
        plats.append(platforms.Platform(pygame.math.Vector2(0, 2), 3, 1))  # 2nd platform that contains (1, 2)
        p = platforms.get_platform_collision(pygame.math.Vector2(1, 2), plats)
        self.assertEqual(p, plats[0])

    def test__get_landing_platform(self):
        plats: List[platforms.Platform] = list()
        start = pygame.math.Vector2(1.942, 1.13)
        end = pygame.math.Vector2(2.204, 0.85)

        # no closest if no platforms
        p = platforms.get_landing_platform(start, end, plats)
        self.assertIsNone(p)

        # no closest if platforms are not relevant
        plats.append(platforms.Platform(pygame.math.Vector2(3, 2), 3))
        p = platforms.get_landing_platform(start, end, plats)
        self.assertIsNone(p)

        # closest that fits
        plats.append(platforms.Platform(pygame.math.Vector2(0.5, 1.1), 3))
        plats.append(platforms.Platform(pygame.math.Vector2(0.5, 1.01), 3))
        plats.append(platforms.Platform(pygame.math.Vector2(0.5, 1.12), 3))
        plats.append(platforms.Platform(pygame.math.Vector2(0.5, 0.9), 3))
        p = platforms.get_landing_platform(start, end, plats)
        self.assertEqual(p, plats[3])

        # no platform if y did not change
        start = pygame.math.Vector2(1.942, 1.0)
        end = pygame.math.Vector2(2.204, 1.0)
        p = platforms.get_landing_platform(start, end, plats)
        self.assertIsNone(p)

    def test__get_support_platform(self):
        plats: List[platforms.Platform] = list()
        pos = pygame.math.Vector2(2, 2)

        # no closest if no platforms
        relevant = platforms.get_support_platform(pos, plats)
        self.assertIsNone(relevant)

        # no closest if platforms are not relevant
        plats.append(platforms.Platform(pygame.math.Vector2(3, 2), 3))
        relevant = platforms.get_support_platform(pos, plats)
        self.assertIsNone(relevant)

        # closest that fits
        plats.append(platforms.Platform(pygame.math.Vector2(1, 1), 3))
        plats.append(platforms.Platform(pygame.math.Vector2(1, 1), 3, height=1))  # yields y_top == 2
        plats.append(platforms.Platform(pygame.math.Vector2(-2, 2), 2))
        plats.append(platforms.Platform(pygame.math.Vector2(0, 2), 3))
        relevant = platforms.get_support_platform(pos, plats)
        self.assertEqual(relevant, plats[2])
