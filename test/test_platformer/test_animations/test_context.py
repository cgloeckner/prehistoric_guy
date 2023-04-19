import unittest

from core import constants
from platformer.animations import actions, context
from platformer import physics, animations


class UnittestListener(context.EventListener):

    def __init__(self):
        self.last = None

    def on_step(self, ani: context.Actor) -> None:
        self.last = ('step', ani)

    def on_climb(self, ani: context.Actor) -> None:
        self.last = ('climb', ani)

    def on_attack(self, ani: context.Actor) -> None:
        self.last = ('attack', ani)

    def on_throw(self, ani: context.Actor) -> None:
        self.last = ('throw', ani)

    def on_died(self, ani: context.Actor) -> None:
        self.last = ('die', ani)


class AnimationSystemTest(unittest.TestCase):

    def setUp(self):
        self.listener = UnittestListener()
        self.ctx = context.Context()
        self.phys_ctx = physics.Context()
        self.sys = context.AnimationSystem(self.listener, self.ctx, self.phys_ctx)

    # ------------------------------------------------------------------------------------------------------------------

    def test__notify_finished(self):
        # movement
        actor = self.ctx.create_actor(1)
        self.phys_ctx.create_actor(1, 2.0, 1.0)
        actor.frame.start(actions.Action.MOVE)
        self.sys.notify_finished(actor)

        self.assertIsNotNone(self.listener.last)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'step')
        self.assertEqual(self.listener.last[1].object_id, actor.object_id)

        # attack
        self.listener.last = None
        actor.frame.start(actions.Action.ATTACK)
        self.sys.notify_finished(actor)

        self.assertIsNotNone(self.listener.last)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'attack')
        self.assertEqual(self.listener.last[1].object_id, actor.object_id)

        # throw
        self.listener.last = None
        actor.frame.start(actions.Action.THROW)
        self.sys.notify_finished(actor)

        self.assertIsNotNone(self.listener.last)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'throw')
        self.assertEqual(self.listener.last[1].object_id, actor.object_id)

        # died
        self.listener.last = None
        actor.frame.start(actions.Action.DIE)
        self.sys.notify_finished(actor)

        self.assertIsNotNone(self.listener.last)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'die')
        self.assertEqual(self.listener.last[1].object_id, actor.object_id)

    def test__update_actor(self):
        actor = self.ctx.create_actor(1)
        self.phys_ctx.create_actor(1, 2.0, 1.0)
        actor.frame.start(actions.Action.CLIMB)
        actor.frame.frame_id = constants.ANIMATION_NUM_FRAMES - 1
        actor.frame.duration_ms = 20
        old_delta_y = actor.oscillate.delta_y
        self.sys.update_actor(actor, 10)

        # oscillation is triggered
        self.assertEqual(actor.oscillate.total_time_ms, 10)
        self.assertNotEqual(actor.oscillate.delta_y, old_delta_y)

        # update for another 10ms
        self.assertIsNone(self.listener.last)
        self.sys.update_actor(actor, 10)

        # finished frame animation behaves correctly
        self.assertEqual(actor.frame.action, actions.Action.HOLD)
        self.assertEqual(actor.frame.frame_id, 0)

        # finished frame animation triggers notify
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'climb')
        self.assertEqual(self.listener.last[1].object_id, actor.object_id)

    def test__update_actor__actor_can_be_busy(self):
        actor = self.ctx.create_actor(1)
        physics_actor = self.phys_ctx.create_actor(1, 2.0, 1.0)

        for action in animations.Action:
            actor.frame.start(action)
            self.sys.update_actor(actor, 10)
            if action in animations.BUSY_ANIMATIONS:
                self.assertFalse(physics_actor.can_climb)
            else:
                self.assertTrue(physics_actor.can_climb)

    def test__update(self):
        self.ctx.create_actor(1)
        self.ctx.create_actor(2)
        self.ctx.create_actor(3)
        self.phys_ctx.create_actor(1, 2.0, 1.0)
        self.phys_ctx.create_actor(2, 2.0, 1.0)
        self.phys_ctx.create_actor(3, 2.0, 1.0)

        # make them move to trigger oscillation too
        for actor in self.ctx.actors:
            actor.frame.start(actions.Action.MOVE)

        self.sys.update(10)
        self.sys.update(15)

        # make sure everybody got updated
        for actor in self.ctx.actors:
            self.assertEqual(actor.oscillate.total_time_ms, 25)
