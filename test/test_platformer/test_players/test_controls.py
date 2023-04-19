import pygame
import unittest

from platformer import physics, animations

from platformer.players import binding, controls


class ControlSystemTest(unittest.TestCase):

    def setUp(self):
        self.ctx = controls.Context()
        self.phys_ctx = physics.Context()
        self.ani_ctx = animations.Context()
        self.sys = controls.ControlsSystem(self.ctx, self.phys_ctx, self.ani_ctx)

    def create_actor(self, object_id: int, x: float, y: float) -> controls.Actor:
        actor = self.ctx.create_actor(object_id=object_id)
        self.phys_ctx.create_actor(object_id=object_id, x=x, y=y)
        self.ani_ctx.create_actor(object_id=object_id)
        return actor

    def test__process_event(self):
        actor1 = self.create_actor(1, 2.0, 1.0)
        actor2 = self.create_actor(1, 2.0, 1.0)

        # propagate attack and moving right
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        self.sys.process_event(event)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        self.sys.process_event(event)
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE)
        self.sys.process_event(event)

        self.assertAlmostEqual(actor1.state.delta.x, 1.0)
        self.assertAlmostEqual(actor2.state.delta.x, 1.0)
        self.assertAlmostEqual(actor1.state.action, binding.Action.ATTACK)
        self.assertAlmostEqual(actor2.state.action, binding.Action.ATTACK)

    # ------------------------------------------------------------------------------------------------------------------

    def test__apply_input__jump_off_ladder_attacking(self):
        actor = self.create_actor(1, 2.0, 1.0)
        phys_actor = self.phys_ctx.actors.get_by_id(actor.object_id)
        ani_actor = self.ani_ctx.actors.get_by_id(actor.object_id)

        phys_actor.on_ladder = self.phys_ctx.create_ladder(2.0, 1.0, 2)
        ani_actor.frame.action = animations.Action.CLIMB

        # jump off ladder attacking
        actor.state.delta.x = 1.0
        actor.state.delta.y = 1.0
        actor.state.action = binding.Action.ATTACK

        print('go')
        self.sys.apply_input(actor)

        self.assertIsNone(phys_actor.on_ladder)
        self.assertAlmostEqual(phys_actor.move.force.x, 1.0)
        self.assertAlmostEqual(phys_actor.move.force.y, 1.0)

        self.assertEqual(ani_actor.frame.action, animations.Action.ATTACK)

    def test__apply_input__no_landing_interrupt(self):
        actor = self.create_actor(1, 2.0, 1.0)
        phys_actor = self.phys_ctx.actors.get_by_id(actor.object_id)
        ani_actor = self.ani_ctx.actors.get_by_id(actor.object_id)

        ani_actor.frame.action = animations.Action.LANDING
        ani_actor.frame.frame_id = 2
        ani_actor.frame.duration_ms = 123

        # attempt anything
        actor.state.delta.x = 1.0
        actor.state.delta.y = 1.0
        actor.state.action = binding.Action.ATTACK

        self.sys.apply_input(actor)

        self.assertIsNone(phys_actor.on_ladder)
        self.assertAlmostEqual(phys_actor.move.force.x, 0.0)
        self.assertAlmostEqual(phys_actor.move.force.y, 0.0)

        self.assertEqual(ani_actor.frame.action, animations.Action.LANDING)
        self.assertEqual(ani_actor.frame.frame_id, 2)
        self.assertEqual(ani_actor.frame.duration_ms, 123)

    def test__apply_input__no_jumping_in_the_air(self):
        actor = self.create_actor(1, 2.0, 1.0)
        phys_actor = self.phys_ctx.actors.get_by_id(actor.object_id)
        ani_actor = self.ani_ctx.actors.get_by_id(actor.object_id)

        phys_actor.move.force.x = 1.0
        phys_actor.move.force.y = -0.4923
        ani_actor.frame.action = animations.Action.JUMP
        ani_actor.frame.frame_id = 2
        ani_actor.frame.duration_ms = 123

        # jump with direction
        actor.state.delta.x = -1.0
        actor.state.delta.y = 1.0
        actor.state.action = binding.Action.NONE

        self.sys.apply_input(actor)

        self.assertAlmostEqual(phys_actor.move.force.x, -1.0)
        self.assertAlmostEqual(phys_actor.move.force.y, -0.4923)

        self.assertEqual(ani_actor.frame.action, animations.Action.JUMP)
        self.assertEqual(ani_actor.frame.frame_id, 2)
        self.assertEqual(ani_actor.frame.duration_ms, 123)

    def test__apply_input__change_direction_during_jump(self):
        actor = self.create_actor(1, 2.0, 1.0)
        phys_actor = self.phys_ctx.actors.get_by_id(actor.object_id)
        ani_actor = self.ani_ctx.actors.get_by_id(actor.object_id)

        phys_actor.move.force.x = 1.0
        phys_actor.move.force.y = -0.4923
        ani_actor.frame.action = animations.Action.JUMP
        ani_actor.frame.frame_id = 2
        ani_actor.frame.duration_ms = 123

        # jump with direction
        actor.state.delta.x = -1.0
        actor.state.action = binding.Action.NONE

        self.sys.apply_input(actor)

        self.assertAlmostEqual(phys_actor.move.force.x, -1.0)
        self.assertAlmostEqual(phys_actor.move.force.y, -0.4923)

        self.assertEqual(ani_actor.frame.action, animations.Action.JUMP)
        self.assertEqual(ani_actor.frame.frame_id, 2)
        self.assertEqual(ani_actor.frame.duration_ms, 123)

    def test__apply_input__can_simply_move_too(self):
        actor = self.create_actor(1, 2.0, 1.0)
        phys_actor = self.phys_ctx.actors.get_by_id(actor.object_id)
        ani_actor = self.ani_ctx.actors.get_by_id(actor.object_id)
        phys_actor.on_platform = self.phys_ctx.create_platform(0.0, 1.0, 4)

        actor.state.delta.x = 1.0
        self.sys.apply_input(actor)

        self.assertAlmostEqual(phys_actor.move.force.x, 1.0)
        self.assertEqual(ani_actor.frame.action, animations.Action.MOVE)
