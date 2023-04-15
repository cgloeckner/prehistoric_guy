import unittest
import pygame
from typing import List

from platformer.physics import actors


def object_id_generator():
    n = 1
    while True:
        yield n
        n += 1


id_generator = object_id_generator()


def create_actor(x: float, y: float, radius: float = 1.0) -> actors.Actor:
    return actors.Actor(object_id=next(id_generator), pos=pygame.math.Vector2(x, y), radius=radius)


class ActorsPhysicsTest(unittest.TestCase):

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
        actor.movement.face_x = -1.0
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
        actor.movement.face_x = 1.0
        result = actor.get_all_faced_actors(actor_list, 2.5)
        self.assertEqual(len(result), 0)
