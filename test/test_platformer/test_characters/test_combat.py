import unittest
from typing import Optional

from core import constants, objectids
from platformer import physics, animations
from platformer.characters import context, combat


class FallingTest(unittest.TestCase):

    def setUp(self):
        self.ctx = context.Context()
        self.phys_ctx = physics.Context()
        self.ani_ctx = animations.Context()

        self.id_generator = objectids.object_id_generator()

    def create_actor(self, object_id: int, x: float, y: float, hp: int = 5, axes: int = 3):
        self.ctx.create_actor(object_id=object_id, max_hit_points=hp, num_axes=axes)
        self.phys_ctx.create_actor(object_id=object_id, x=x, y=y)

    def create_projectile(self, x: float, y: float, from_actor: Optional[physics.Actor], speed: float,
                          object_type: constants.ObjectType):
        object_id = next(self.id_generator)
        proj = self.phys_ctx.create_projectile(object_id=object_id, x=x, y=y, object_type=object_type,
                                               from_actor=from_actor)
        proj.move.speed = speed
        self.ani_ctx.create_projectile(object_id=object_id)

    def test__get_falling_from(self):
        self.create_actor(1, 1.0, 1.0)
        self.create_actor(3, 1.6, 1.0)
        self.create_actor(2, 1.5, 1.0)
        self.create_actor(4, 2.5, 1.0)

        in_range = combat.query_melee_range(self.ctx.actors.get_by_id(1), self.ctx, self.phys_ctx)
        self.assertEqual(len(in_range), 2)
        self.assertEqual(in_range[0].object_id, 2)
        self.assertEqual(in_range[1].object_id, 3)

    def test__attack_enemy(self):
        self.create_actor(1, 1.0, 1.0)
        self.create_actor(2, 1.6, 1.0)

        # can hit
        victim = self.ctx.actors.get_by_id(2)
        result = combat.attack_enemy(2, victim)
        self.assertTrue(result)
        self.assertEqual(victim.hit_points, 3)

        # can kill
        result = combat.attack_enemy(7, victim)
        self.assertTrue(result)
        self.assertEqual(victim.hit_points, 0)

        # cannot hit the dead
        result = combat.attack_enemy(1, victim)
        self.assertFalse(result)

    def test__throw_object(self):
        self.create_actor(1, 1.0, 1.0)

        combat.throw_object(self.ctx.actors.get_by_id(1), 12.0, constants.ObjectType.FOOD, self.phys_ctx,
                            self.create_projectile)
