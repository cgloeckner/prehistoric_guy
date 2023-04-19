import unittest

from platformer import physics, animations
from platformer.characters import context, falling


class FallingTest(unittest.TestCase):

    def setUp(self):
        self.ctx = context.Context()
        self.phys_ctx = physics.Context()

    def test__get_falling_from(self):
        actor = self.ctx.create_actor(1, 5, 3)
        phys = self.phys_ctx.create_actor(1, 3, 4)

        falling.set_falling_from(actor, phys)
        self.assertEqual(actor.falling_from, phys.pos)
        self.assertNotEqual(id(actor.falling_from), id(phys.pos))

    def test__set_falling_from(self):
        actor = self.ctx.create_actor(1, 5, 3)
        phys = self.phys_ctx.create_actor(1, 3, 4)

        # no height if wasn't set previously
        height = falling.get_falling_height(actor, phys.pos)
        self.assertEqual(height, 0.0)

        # calculate delta-y
        falling.set_falling_from(actor, phys)
        phys.pos.y -= 3.5
        height = falling.get_falling_height(actor, phys.pos)
        self.assertEqual(height, 3.5)

    def test__is_dangerous_height(self):
        self.assertFalse(falling.is_dangerous_height(1))
        self.assertTrue(falling.is_dangerous_height(5))

    def test__get_falling_damage(self):
        damage = falling.get_falling_damage(1)
        self.assertEqual(damage, 0)

        damage = falling.get_falling_damage(10)
        self.assertEqual(damage, 10 // 4)

    def test__apply_landing(self):
        actor = self.ctx.create_actor(1, 5, 3)
        phys = self.phys_ctx.create_actor(1, 3, 4)
        falling.set_falling_from(actor, phys)
        phys.pos.y -= 0.5

        # minor fall
        result, damage = falling.apply_landing(actor, phys)
        self.assertEqual(result, animations.Action.IDLE)

        # more intense fall
        phys.pos.y = 4
        falling.set_falling_from(actor, phys)
        phys.pos.y = 2
        result, damage = falling.apply_landing(actor, phys)
        self.assertEqual(result, animations.Action.LANDING)
        self.assertEqual(actor.hit_points, 5)

        # really dangerous (=damaging) fall
        phys.pos.y = 5
        falling.set_falling_from(actor, phys)
        phys.pos.y = 0
        result, damage = falling.apply_landing(actor, phys)
        self.assertEqual(result, animations.Action.LANDING)
        self.assertEqual(actor.hit_points, 4)

        # fall to death
        phys.pos.y = 100
        falling.set_falling_from(actor, phys)
        phys.pos.y = 0
        result, damage = falling.apply_landing(actor, phys)
        self.assertEqual(result, animations.Action.LANDING)
        self.assertEqual(actor.hit_points, 0)
