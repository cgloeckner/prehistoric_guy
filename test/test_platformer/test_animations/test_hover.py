import pygame
import unittest

from platformer import physics
from platformer.animations import hover


class PlatformHoveringTest(unittest.TestCase):

    def test__update_actors(self):
        platform = physics.Platform(pos=pygame.math.Vector2(0.0, 0.0), width=4)
        platform.hover.x = physics.HoverType.SIN
        platform.hover.y = physics.HoverType.SIN
        platform.hover.update(50)

        actors = list()
        actors.append(physics.Actor(1, pos=pygame.math.Vector2(1.0, 0.0)))
        actors.append(physics.Actor(2, pos=pygame.math.Vector2(2.0, 0.0)))
        actors.append(physics.Actor(3, pos=pygame.math.Vector2(3.0, 0.0)))
        actors[0].on_platform = platform
        actors[2].on_platform = platform

        hover.update_actors(platform, actors)

        self.assertGreater(actors[0].pos.x, 1.0)
        self.assertGreater(actors[0].pos.y, 0.0)

        self.assertAlmostEqual(actors[1].pos.x, 2.0)
        self.assertAlmostEqual(actors[1].pos.y, 0.0)

        self.assertGreater(actors[2].pos.x, 2.0)
        self.assertGreater(actors[2].pos.y, 0.0)
