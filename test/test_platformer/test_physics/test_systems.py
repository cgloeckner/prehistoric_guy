import unittest

from core import constants
from platformer.physics import actors, platforms, objects, projectiles, ladders, systems, context


class UnittestListener(context.EventListener):
    def __init__(self):
        self.last = None

    def on_grab(self, actor: actors.Actor) -> None:
        self.last = ('grab', actor)

    def on_release(self, actor: actors.Actor) -> None:
        self.last = ('release', actor)

    def on_falling(self, actor: actors.Actor) -> None:
        self.last = ('falling', actor)

    def on_landing(self, actor: actors.Actor) -> None:
        self.last = ('landing', actor)

    def on_collision(self, actor: actors.Actor, platform: platforms.Platform) -> None:
        self.last = ('collision', actor, platform)

    def on_impact_platform(self, proj: projectiles.Projectile, platform: platforms.Platform) -> None:
        self.last = ('impact_platform', proj, platform)

    def on_impact_actor(self, proj: projectiles.Projectile, actor: actors.Actor) -> None:
        self.last = ('impact_actor', proj, actor)

    def on_touch_object(self, actor: actors.Actor, obj: objects.Object) -> None:
        self.last = ('touch_object', actor, obj)

    def on_touch_actor(self, actor: actors.Actor, other: actors.Actor) -> None:
        self.last = ('touch_actor', actor, other)


# ----------------------------------------------------------------------------------------------------------------------


class ActorSystemsTest(unittest.TestCase):

    def setUp(self):
        self.listener = UnittestListener()
        self.context = context.Context()
        self.system = systems.ActorSystem(self.listener, self.context)

    def test__handle_ladders(self):
        actor = self.context.create_actor(1, x=2.0, y=1.0 + constants.OBJECT_RADIUS)
        ladder = self.context.create_ladder(x=2.0, y=1.0, height=4)

        # grab slightly above bottom (since bottom pos itself does not lead to grabbing)
        self.system.handle_ladders(actor)
        self.assertEqual(actor.on_ladder, ladder)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 2)
        self.assertEqual(self.listener.last[0], 'grab')
        self.assertEqual(self.listener.last[1], actor)

        # keeps grabbed
        self.listener.last = None
        self.system.handle_ladders(actor)
        self.assertEqual(actor.on_ladder, ladder)
        self.assertIsNone(self.listener.last)

        # release
        self.listener.last = None
        actor.pos.x += constants.OBJECT_RADIUS + 0.01
        self.system.handle_ladders(actor)
        self.assertIsNone(actor.on_ladder)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 2)
        self.assertEqual(self.listener.last[0], 'release')
        self.assertEqual(self.listener.last[1], actor)

        # keeps released
        self.listener.last = None
        self.system.handle_ladders(actor)
        self.assertIsNone(actor.on_ladder)

        # grab at top
        actor.pos = ladder.pos.copy()
        actor.pos.y += ladder.height
        self.system.handle_ladders(actor)
        self.assertEqual(actor.on_ladder, ladder)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 2)
        self.assertEqual(self.listener.last[0], 'grab')
        self.assertEqual(self.listener.last[1], actor)

    def test__handle_gravity(self):
        actor = self.context.create_actor(1, x=2.0, y=1.0)

        # starts falling
        self.system.handle_gravity(actor, 10)
        self.assertLess(actor.move.force.y, 0.0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 2)
        self.assertEqual(self.listener.last[0], 'falling')
        self.assertEqual(self.listener.last[1], actor)

        # grabbed ladder stops fall
        actor.on_ladder = self.context.create_ladder(x=2.0, y=1.5, height=4)
        self.listener.last = None
        self.system.handle_gravity(actor, 10)
        self.assertIsNone(self.listener.last)

        # jump off ladder
        actor.move.force.x = 1.0
        actor.move.force.y = 1.0
        self.system.handle_gravity(actor, 10)
        self.assertGreater(actor.move.force.y, 0.0)
        self.assertIsNone(self.listener.last)

        # turn falling
        actor.on_ladder = None
        actor.move.force.y = 0.01
        self.system.handle_gravity(actor, 10)
        self.assertLess(actor.move.force.y, 0.0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 2)
        self.assertEqual(self.listener.last[0], 'falling')
        self.assertEqual(self.listener.last[1], actor)

        # being on a platform stops falling
        self.listener.last = None
        actor.on_platform = self.context.create_platform(x=0, y=1.5, width=5)
        self.system.handle_gravity(actor, 10)
        self.assertIsNone(self.listener.last)

    def test__handle_movement(self):
        actor = self.context.create_actor(1, x=2.0, y=1.0)

        # no motion causes no position change
        old_pos = self.system.handle_movement(actor, 10)
        self.assertEqual(old_pos, actor.pos)

        # force is applied
        actor.move.force.x = 1.0
        actor.move.force.y = 1.0
        old_pos = self.system.handle_movement(actor, 10)
        self.assertGreater(actor.pos.x, old_pos.x)
        self.assertGreater(actor.pos.y, old_pos.y)

        # force can be applied while on a ladder
        actor.on_ladder = self.context.create_ladder(x=2.0, y=1.0, height=2)
        old_pos = self.system.handle_movement(actor, 10)
        self.assertGreater(actor.pos.x, old_pos.x)
        self.assertGreater(actor.pos.y, old_pos.y)

        # left the ladder during this motion
        self.assertIsNone(actor.on_ladder)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 2)
        self.assertEqual(self.listener.last[0], 'release')
        self.assertEqual(self.listener.last[1], actor)

    def test__handle_landing(self):
        actor = self.context.create_actor(1, x=2.0, y=0.9)
        old_pos = actor.pos.copy()
        old_pos.y += 0.2

        # no platform means no landing
        self.system.handle_landing(actor, old_pos)
        self.assertIsNone(self.listener.last)

        # platform causes anchoring
        actor.move.force.x = 1.0
        actor.move.force.y = 1.0
        platform = self.context.create_platform(x=1.0, y=1.0, width=5)
        self.system.handle_landing(actor, old_pos)
        self.assertEqual(actor.on_platform, platform)
        self.assertAlmostEqual(actor.pos.x, 2.0)
        self.assertAlmostEqual(actor.pos.y, 1.0)
        self.assertAlmostEqual(actor.move.force.x, 0.0)
        self.assertAlmostEqual(actor.move.force.y, 0.0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 2)
        self.assertEqual(self.listener.last[0], 'landing')
        self.assertEqual(self.listener.last[1], actor)

        # anchoring can happen without falling
        self.listener.last = None
        actor.pos.y = 1.0
        old_pos = actor.pos.copy()
        platform = self.context.create_platform(x=1.0, y=1.0, width=5)
        self.system.handle_landing(actor, old_pos)
        self.assertEqual(actor.on_platform, platform)
        self.assertIsNone(self.listener.last)

    def test__handle_platform_collision(self):
        actor = self.context.create_actor(1, x=2.0, y=1.0)
        old_pos = actor.pos.copy()

        # no platform means no collision
        self.system.handle_landing(actor, old_pos)
        self.assertIsNone(self.listener.last)

        # platform causes collision
        old_pos.x = 1.0
        platform = self.context.create_platform(x=2.0, y=0.0, width=3, height=2)
        self.system.handle_platform_collision(actor, old_pos)
        self.assertAlmostEqual(actor.pos.x, 1.0)
        self.assertAlmostEqual(actor.pos.y, 1.0)
        self.assertAlmostEqual(actor.move.force.x, 0.0)
        self.assertAlmostEqual(actor.move.force.y, 0.0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 3)
        self.assertEqual(self.listener.last[0], 'collision')
        self.assertEqual(self.listener.last[1], actor)
        self.assertEqual(self.listener.last[2], platform)

    def test__handle_object_collision(self):
        actor = self.context.create_actor(1, x=2.0, y=1.0)

        # no objects means no collision
        self.system.handle_object_collision(actor)
        self.assertIsNone(self.listener.last)

        # object can be touched
        obj = self.context.create_object(x=2.1, y=1.0, object_type=constants.ObjectType.FOOD)
        self.system.handle_object_collision(actor)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 3)
        self.assertEqual(self.listener.last[0], 'touch_object')
        self.assertEqual(self.listener.last[1], actor)
        self.assertEqual(self.listener.last[2], obj)

    def test__handle_actor_collision(self):
        actor = self.context.create_actor(1, x=2.0, y=1.0)

        # no other actor means no collision
        self.system.handle_object_collision(actor)
        self.assertIsNone(self.listener.last)

        # other actor can be touched
        other = self.context.create_actor(2, x=2.1, y=1.0)
        self.system.handle_actor_collision(actor)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 3)
        self.assertEqual(self.listener.last[0], 'touch_actor')
        self.assertEqual(self.listener.last[1], actor)
        self.assertEqual(self.listener.last[2], other)

    # ------------------------------------------------------------------------------------------------------------------

    def test_can_release_off_ladder(self):
        actor = self.context.create_actor(1, 2.0, 4.0)
        actor.on_ladder = self.context.create_ladder(2.0, 2.0, 5)
        actor.move.force.x = 1.0
        actor.move.force.y = 0.0

        for i in range(10):
            self.system.update(15)

        self.assertGreater(actor.pos.x, 2.0)
        self.assertLess(actor.pos.y, 4.0)

    def test_can_jump_off_ladder(self):
        actor = self.context.create_actor(1, 2.0, 4.0)
        actor.on_ladder = self.context.create_ladder(2.0, 2.0, 5)
        actor.move.force.x = 1.0
        actor.move.force.y = 1.0

        for i in range(10):
            self.system.update(15)

        self.assertGreater(actor.pos.x, 2.0)
        self.assertGreater(actor.pos.y, 4.0)


# ----------------------------------------------------------------------------------------------------------------------


class ProjectileSystemsTest(unittest.TestCase):

    def setUp(self):
        self.listener = UnittestListener()
        self.context = context.Context()
        self.system = systems.ProjectileSystem(self.listener, self.context)

    def test__handle_movement(self):
        proj = self.context.create_projectile(object_id=10, x=2.0, y=1.0)
        proj.move.force.x = 1.0
        proj.move.force.y = -1.0

        old_pos = self.system.handle_movement(proj, 10)
        self.assertGreater(proj.pos.x, old_pos.x)
        self.assertLess(proj.pos.y, old_pos.y)

    def test__handle_platform_collision(self):
        proj = self.context.create_projectile(object_id=10, x=2.0, y=2.0)
        proj.move.force.x = 1.0
        proj.move.force.y = -0.1
        old_pos = proj.pos.copy()
        old_pos.x = 1.0
        old_pos.y = 2.0

        # no platform means no collision
        self.system.handle_platform_collision(proj, old_pos)
        self.assertIsNone(self.listener.last)

        # projectile can collide with platform
        platform = self.context.create_platform(x=1.0, y=1.0, width=6, height=3)
        self.system.handle_platform_collision(proj, old_pos)
        self.assertAlmostEqual(proj.pos.x, old_pos.x)
        self.assertAlmostEqual(proj.pos.y, old_pos.y)
        self.assertAlmostEqual(proj.move.force.x, 0.0)
        self.assertAlmostEqual(proj.move.force.y, 0.0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 3)
        self.assertEqual(self.listener.last[0], 'impact_platform')
        self.assertEqual(self.listener.last[1], proj)
        self.assertEqual(self.listener.last[2], platform)
        self.assertNotEqual(id(proj.pos), id(old_pos))

        # projectile can vertically impact on a platform
        proj.pos.x = 2.0
        proj.pos.y = 0.9
        old_pos.x = 2.0
        old_pos.y = 1.3
        platform.pos.y = -2.0
        self.system.handle_platform_collision(proj, old_pos)
        self.assertAlmostEqual(proj.pos.x, 2.0)
        self.assertAlmostEqual(proj.pos.y, 1.0)
        self.assertAlmostEqual(proj.move.force.x, 0.0)
        self.assertAlmostEqual(proj.move.force.y, 0.0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 3)
        self.assertEqual(self.listener.last[0], 'impact_platform')
        self.assertEqual(self.listener.last[1], proj)
        self.assertEqual(self.listener.last[2], platform)

    def test__handle_actor_collision(self):
        proj = self.context.create_projectile(object_id=10, x=2.0, y=2.0)
        proj.move.force.x = 1.0

        # no actor means no collision
        self.system.handle_actor_collision(proj)
        self.assertIsNone(self.listener.last)

        # actor can be hit
        actor = self.context.create_actor(1, x=2.2, y=2.0)
        self.system.handle_actor_collision(proj)
        self.assertEqual(proj.move.force.x, 0.0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(len(self.listener.last), 3)
        self.assertEqual(self.listener.last[0], 'impact_actor')
        self.assertEqual(self.listener.last[1], proj)
        self.assertEqual(self.listener.last[2], actor)
