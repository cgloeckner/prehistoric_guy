import unittest
import pygame
from typing import List

from core import objectids
from platformer.physics import actors
from platformer.physics import platforms


def create_actor(x: float, y: float, radius: float = 1.0) -> actors.Actor:
    return actors.Actor(object_id=next(objectids.generator), pos=pygame.math.Vector2(x, y), radius=radius)


class ActorsPhysicsTest(unittest.TestCase):

    def test__can_fall(self):
        actor = create_actor(2, 1, 0.5)

        # can fall if neither on ladder nor platform
        self.assertTrue(actor.can_fall())

        # cannot fall if on a ladder
        actor.on_ladder = object()
        self.assertFalse(actor.can_fall())

        # cannot fall if on a ladder and a platform
        actor.on_platform = object()
        self.assertFalse(actor.can_fall())

        # cannot fall if on a platform
        actor.on_ladder = None
        self.assertFalse(actor.can_fall())

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_all_faced_actors(self):
        actor = create_actor(2, 1, 0.5)
        actor_list: List[actors.Actor] = list()

        # empty sequence is handled fine
        result = actor.get_all_faced_actors(actor_list, 3.5)
        self.assertEqual(len(result), 0)

        # ignores himself
        actor_list.append(actor)
        result = actor.get_all_faced_actors(actor_list, 3.5)
        self.assertEqual(len(result), 0)

        actor2 = create_actor(x=3.5, y=0.5)
        actor3 = create_actor(x=3, y=1.5)
        actor4 = create_actor(x=0.5, y=0.5)
        actor5 = create_actor(x=1, y=1.5)
        actor_list.append(actor2)
        actor_list.append(actor3)
        actor_list.append(actor4)
        actor_list.append(actor5)

        # closest actor to the right
        result = actor.get_all_faced_actors(actor_list, 3.5)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], actor3)
        self.assertEqual(result[1], actor2)

        # closest actor to the left
        actor.move.face_x = -1.0
        result = actor.get_all_faced_actors(actor_list, 2.5)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], actor5)
        self.assertEqual(result[1], actor4)

        # ignore actors to the left
        actor4.pos.x = -10
        actor5.pos.x = -10
        result = actor.get_all_faced_actors(actor_list, 2.5)
        self.assertEqual(len(result), 0)

        # ignore actors to the left
        actor2.pos.x = 15
        actor3.pos.x = 15
        actor4.pos.x = 0.5
        actor5.pos.x = 1
        actor.move.face_x = 1.0
        result = actor.get_all_faced_actors(actor_list, 2.5)
        self.assertEqual(len(result), 0)

    # ------------------------------------------------------------------------------------------------------------------

    def test__land_on_platform(self):
        actor = create_actor(3, 2, 0.5)
        platform = platforms.Platform(pygame.math.Vector2(0, 1), 4)
        actor.land_on_platform(platform, pygame.math.Vector2(2, 0))

        self.assertAlmostEqual(actor.pos.x, 2.5)
        self.assertAlmostEqual(actor.pos.y, 1.0)
        self.assertAlmostEqual(actor.move.force.x, 0.0)
        self.assertAlmostEqual(actor.move.force.y, 0.0)
        self.assertEqual(actor.on_platform, platform)

    # ------------------------------------------------------------------------------------------------------------------

    def test__collide_with_platform(self):
        actor = create_actor(1, 0, 0.5)
        platform = platforms.Platform(pygame.math.Vector2(1, 1), 3, 3)
        old_pos = pygame.math.Vector2(-1, 2)
        actor.collide_with_platform(platform, old_pos)

        self.assertAlmostEqual(actor.pos.x, -1.0)
        self.assertAlmostEqual(actor.pos.y, 2.0)
        self.assertAlmostEqual(actor.move.force.x, 0.0)
        self.assertAlmostEqual(actor.move.force.y, 0.0)
        self.assertEqual(actor.on_platform, platform)
        self.assertNotEqual(id(actor.pos), id(old_pos))
