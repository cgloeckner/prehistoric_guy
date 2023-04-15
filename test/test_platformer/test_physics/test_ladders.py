import unittest
import pygame
from typing import List, Tuple

from platformer.physics.constants import *
from platformer.physics import ladders


class LadderPhysicsTest(unittest.TestCase):

    # Case 1: points within ladder
    # NOTE: y is the bottom, so y + height leads to the bottom
    def test__is_in_reach_of__1(self):
        ladder = ladders.Ladder(pygame.math.Vector2(2.5, 3), 4)

        # bottom end is not in reach
        self.assertFalse(ladder.is_in_reach_of(pygame.math.Vector2(2.5, 3)))
        # mid/top end are in reach
        self.assertTrue(ladder.is_in_reach_of(pygame.math.Vector2(2.5, 3.01)))
        self.assertTrue(ladder.is_in_reach_of(pygame.math.Vector2(2.5, 7)))

    # Case 2: points within ladder +/- radius
    def test__is_in_reach_of__2(self):
        ladder = ladders.Ladder(pygame.math.Vector2(2.5, 3), 4)

        self.assertTrue(ladder.is_in_reach_of(pygame.math.Vector2(2.5 - OBJECT_RADIUS, 4)))
        self.assertTrue(ladder.is_in_reach_of(pygame.math.Vector2(2.5 + OBJECT_RADIUS, 4)))

    # Case 3: points outside ladder +/- radius
    def test__is_in_reach_of__3(self):
        ladder = ladders.Ladder(pygame.math.Vector2(2.5, 3), 4)

        # top/bottom
        self.assertFalse(ladder.is_in_reach_of(pygame.math.Vector2(2.5, 3 - 0.01)))
        self.assertFalse(ladder.is_in_reach_of(pygame.math.Vector2(2.5, 8 + 0.01)))

        # left/right
        self.assertFalse(ladder.is_in_reach_of(pygame.math.Vector2(2.5 - OBJECT_RADIUS - 0.01, 4)))
        self.assertFalse(ladder.is_in_reach_of(pygame.math.Vector2(2.5 + OBJECT_RADIUS + 0.02, 4)))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: actor in the middle
    def test__within_ladder__1(self):
        ladder = ladders.Ladder(pygame.math.Vector2(2.5, 3), 4)
        pos = pygame.math.Vector2(2.5, 4.25)

        self.assertTrue(ladder.contains_point(pos))

    # Case 2: actor at the top
    def test__within_ladder__2(self):
        ladder = ladders.Ladder(pygame.math.Vector2(2.5, 3), 4)
        pos = pygame.math.Vector2(2.5, 7)

        self.assertFalse(ladder.contains_point(pos))

    # Case 3: actor at the bottom
    def test__within_ladder__3(self):
        ladder = ladders.Ladder(pygame.math.Vector2(2.5, 3), 4)
        pos = pygame.math.Vector2(2.5, 2)

        self.assertFalse(ladder.contains_point(pos))

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_closest_ladder_in_reach(self):
        ladds: List[ladders.Ladder] = list()
        pos = pygame.math.Vector2(1.942, 1.13)

        # no closest if no ladders
        p = ladders.get_closest_ladder_in_reach(pos, ladds)
        self.assertIsNone(p)

        # no closest if ladders are not relevant
        ladds.append(ladders.Ladder(pygame.math.Vector2(3, 2), 3))
        p = ladders.get_closest_ladder_in_reach(pos, ladds)
        self.assertIsNone(p)

        # closest that fits
        ladds.append(ladders.Ladder(pygame.math.Vector2(2, 1), 3))
        ladds.append(ladders.Ladder(pygame.math.Vector2(2.05, 1), 3))
        ladds.append(ladders.Ladder(pygame.math.Vector2(1.98, 1), 3))
        ladds.append(ladders.Ladder(pygame.math.Vector2(2.13, 1), 3))
        p = ladders.get_closest_ladder_in_reach(pos, ladds)
        self.assertEqual(p, ladds[3])
