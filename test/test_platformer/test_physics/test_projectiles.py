import unittest
import pygame

from core import objectids
from platformer.physics import actors, platforms, projectiles, context


generator = objectids.object_id_generator()


class ProjectilePhysicsTest(unittest.TestCase):

    def setUp(self) -> None:
        self.ctx = context.Context()

    def test__can_hit(self):
        actor = self.ctx.create_actor(1, 2, 1,)
        actor2 = self.ctx.create_actor(2, 4, 1)
        proj = self.ctx.create_projectile(0, 3, 1)

        # regular case
        self.assertTrue(proj.can_hit(actor))
        self.assertTrue(proj.can_hit(actor2))

        # cannot hit if origin
        proj.from_actor = actor2
        self.assertTrue(proj.can_hit(actor))
        self.assertFalse(proj.can_hit(actor2))

        # cannot hit if actor disabled
        actor.can_collide = False
        self.assertFalse(proj.can_hit(actor))
        self.assertFalse(proj.can_hit(actor2))

    def test__land_on_platform(self):
        plat = self.ctx.create_platform(0, 0, 10)
        proj = self.ctx.create_projectile(0, 2, -0.5)
        proj.move.force.x = 1.0
        proj.move.force.y = -0.5
        old_pos = pygame.math.Vector2(1.95, -0.3)

        # not landing
        proj.land_on_platform(plat, old_pos)
        self.assertNotAlmostEqual(proj.pos.y, plat.pos.y)
        self.assertAlmostEqual(proj.move.force.x, 1.0)
        self.assertAlmostEqual(proj.move.force.y, -0.5)

        # regular case
        old_pos = pygame.math.Vector2(1.95, 0.3)
        proj.land_on_platform(plat, old_pos)
        self.assertAlmostEqual(proj.pos.y, plat.pos.y)
        self.assertAlmostEqual(proj.move.force.x, 0.0)
        self.assertAlmostEqual(proj.move.force.y, 0.0)

    def test__collide_with_platform(self):
        proj = self.ctx.create_projectile(0, 2, -0.5)
        proj.move.force.x = 1.0
        proj.move.force.y = -0.5

        old_pos = pygame.math.Vector2(1.95, 0.3)
        proj.collide_with_platform(old_pos)

        self.assertAlmostEqual(proj.pos.x, old_pos.x)
        self.assertAlmostEqual(proj.pos.y, old_pos.y)
        self.assertAlmostEqual(proj.move.force.x, 0.0)
        self.assertAlmostEqual(proj.move.force.y, 0.0)
