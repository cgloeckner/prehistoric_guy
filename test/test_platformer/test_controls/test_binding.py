import pygame
import unittest

from platformer import physics, animations

from platformer.controls import binding


class InputStateTest(unittest.TestCase):

    def setUp(self) -> None:
        self.bind = binding.Keybinding()

        self.keys = set()

    def keys_test(self, value):
        return value in self.keys

    def tearDown(self) -> None:
        pygame.quit()

    def test__reset(self):
        state = binding.InputState()
        self.assertEqual(state.delta.x, 0.0)
        self.assertEqual(state.delta.y, 0.0)
        self.assertEqual(state.action, binding.Action.NONE)

        state.delta.x = 3
        state.delta.y = -2
        state.action = binding.Action.THROW

        state.reset()
        self.assertEqual(state.delta.x, 0.0)
        self.assertEqual(state.delta.y, 0.0)
        self.assertEqual(state.action, binding.Action.NONE)

    def test__process_event_action(self):
        state = binding.InputState()

        # press attack key
        event = pygame.event.Event(pygame.KEYDOWN, key=self.bind.attack_key)
        state.process_event(self.bind, event)
        self.assertEqual(state.attack_held_ms, 0)
        self.assertEqual(state.action, binding.Action.NONE)

        # held key
        event = pygame.event.Event(pygame.KEYDOWN, key=self.bind.attack_key)
        state.process_event(self.bind, event)
        self.assertEqual(state.attack_held_ms, 0)

        state.attack_held_ms += 150
        # release key for short time -> attack
        event = pygame.event.Event(pygame.KEYUP, key=self.bind.attack_key)
        state.process_event(self.bind, event)
        self.assertEqual(state.attack_held_ms, -1)
        self.assertEqual(state.action, binding.Action.ATTACK)

        state.attack_held_ms = binding.THROW_THRESHOLD
        # release key for longer timer -> throw
        event = pygame.event.Event(pygame.KEYUP, key=self.bind.attack_key)
        state.process_event(self.bind, event)
        self.assertEqual(state.attack_held_ms, -1)
        self.assertEqual(state.action, binding.Action.THROW)

        # another key up does hit release attack
        state.reset()
        event = pygame.event.Event(pygame.KEYDOWN, key=self.bind.attack_key)
        state.process_event(self.bind, event)
        state.attack_held_ms = 13
        event = pygame.event.Event(pygame.KEYUP, key=self.bind.up_key)
        state.process_event(self.bind, event)
        self.assertEqual(state.attack_held_ms, 13)

    def test__process_event_movement(self):
        # press attack key (no effect)
        self.keys.add(self.bind.attack_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 0)
        self.assertEqual(delta.y, 0)

        # press left key
        self.keys.add(self.bind.left_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, -1)
        self.assertEqual(delta.y, 0)

        # add right key
        self.keys.add(self.bind.right_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 0)
        self.assertEqual(delta.y, 0)

        # release left key
        self.keys.remove(self.bind.left_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 1)
        self.assertEqual(delta.y, 0)

        # release right key
        self.keys.remove(self.bind.right_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 0)
        self.assertEqual(delta.y, 0)

        # press up key
        self.keys.add(self.bind.up_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 0)
        self.assertEqual(delta.y, 1)

        # add down key
        self.keys.add(self.bind.down_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 0)
        self.assertEqual(delta.y, 0)

        # release up key
        self.keys.remove(self.bind.up_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 0)
        self.assertEqual(delta.y, -1)

        # release down key
        self.keys.remove(self.bind.down_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 0)
        self.assertEqual(delta.y, 0)

        # up right
        self.keys.add(self.bind.up_key)
        self.keys.add(self.bind.right_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 1)
        self.assertEqual(delta.y, 1)

        # down right
        self.keys.remove(self.bind.up_key)
        self.keys.add(self.bind.down_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, 1)
        self.assertEqual(delta.y, -1)

        # down left
        self.keys.remove(self.bind.right_key)
        self.keys.add(self.bind.left_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, -1)
        self.assertEqual(delta.y, -1)

        # up left
        self.keys.remove(self.bind.down_key)
        self.keys.add(self.bind.up_key)
        delta = self.bind.get_movement(self.keys_test)
        self.assertEqual(delta.x, -1)
        self.assertEqual(delta.y, 1)

    def test__get_throwing_progress(self):
        state = binding.InputState()

        # key not pressed
        progress = state.get_throwing_progress()
        self.assertAlmostEqual(progress, 0.0, places=2)

        # key just pressed
        state.attack_held_ms = 0
        progress = state.get_throwing_progress()
        self.assertAlmostEqual(progress, 0.0, places=2)

        # pressed some ms ago
        state.attack_held_ms = 25
        progress = state.get_throwing_progress()
        self.assertAlmostEqual(progress, 0.052, places=2)

        # close to finish
        state.attack_held_ms += 250
        progress = state.get_throwing_progress()
        self.assertAlmostEqual(progress, 0.573, places=2)

        # finished
        state.attack_held_ms = binding.THROW_THRESHOLD
        progress = state.get_throwing_progress()
        self.assertAlmostEqual(progress, 1.0, places=2)

        # way beyond finish
        state.attack_held_ms += 250
        self.assertAlmostEqual(progress, 1.0, places=2)

    def test__update(self):
        state = binding.InputState()

        # default: no attack held
        state.update_action(15)
        self.assertEqual(state.attack_held_ms, -1)

        # step attack held a bit
        state.attack_held_ms = 0
        state.update_action(15)
        self.assertEqual(state.attack_held_ms, 15)
        self.assertEqual(state.action, binding.Action.NONE)

        # complete throw threshold without releasing
        state.attack_held_ms = binding.THROW_THRESHOLD - 1
        state.update_action(1)
        self.assertEqual(state.attack_held_ms, 0)
        self.assertEqual(state.action, binding.Action.THROW)

        # exceed threshold resets because it fires
        state.action = binding.Action.NONE
        state.attack_held_ms = binding.THROW_THRESHOLD + 7
        state.update_action(15)
        self.assertEqual(state.attack_held_ms, 0)
        self.assertEqual(state.action, binding.Action.THROW)

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_next_animation__jump(self):
        state = binding.InputState()

        # can jump off a ladder attacking
        state.delta.x = 1
        state.delta.y = 1
        state.action = binding.Action.ATTACK
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.ATTACK)

        # can jump off a ladder throwing
        state.delta.x = 1
        state.delta.y = 1
        state.action = binding.Action.THROW
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.THROW)

        # can jump off a ladder without action
        state.delta.x = 1
        state.delta.y = 1
        state.action = binding.Action.NONE
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.JUMP)

    def test__get_next_animation__climb(self):
        state = binding.InputState()

        # can climb a ladder and attack
        state.delta.x = 0
        state.delta.y = -1
        state.action = binding.Action.ATTACK
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.ATTACK)

        # can climb a ladder and throw
        state.delta.x = 0
        state.delta.y = -1
        state.action = binding.Action.THROW
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.THROW)

        # can climb a ladder without an action
        state.delta.x = 0
        state.delta.y = -1
        state.action = binding.Action.NONE
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.CLIMB)

    def test__get_next_animation__hold(self):
        state = binding.InputState()

        # can hold on a ladder and attack
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.ATTACK
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.ATTACK)

        # can hold on a ladder and throw
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.THROW
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.THROW)

        # can hold on a ladder without an action
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.NONE
        ani = state.get_next_animation(is_on_ladder=True, is_on_platform=False)
        self.assertEqual(ani, animations.Action.HOLD)

    def test__get_next_animation__move(self):
        state = binding.InputState()

        # move falling and attack
        state.delta.x = -1
        state.delta.y = 0
        state.action = binding.Action.ATTACK
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=False)
        self.assertEqual(ani, animations.Action.ATTACK)

        # move falling and throw
        state.delta.x = 1
        state.delta.y = 0
        state.action = binding.Action.THROW
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=False)
        self.assertEqual(ani, animations.Action.THROW)

        # move falling without an action
        state.delta.x = 1
        state.delta.y = 0
        state.action = binding.Action.NONE
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=False)
        self.assertEqual(ani, animations.Action.JUMP)

        # move and attack
        state.delta.x = -1
        state.delta.y = 0
        state.action = binding.Action.ATTACK
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=True)
        self.assertEqual(ani, animations.Action.ATTACK)

        # move and throw
        state.delta.x = 1
        state.delta.y = 0
        state.action = binding.Action.THROW
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=True)
        self.assertEqual(ani, animations.Action.THROW)

        # move without an action
        state.delta.x = 1
        state.delta.y = 0
        state.action = binding.Action.NONE
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=True)
        self.assertEqual(ani, animations.Action.MOVE)

    def test__get_next_animation__idle(self):
        state = binding.InputState()

        # idle falling and attack
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.ATTACK
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=False)
        self.assertEqual(ani, animations.Action.ATTACK)

        # idle falling and throw
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.THROW
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=False)
        self.assertEqual(ani, animations.Action.THROW)

        # idle falling without an action
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.NONE
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=False)
        self.assertEqual(ani, animations.Action.JUMP)

        # idle and attack
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.ATTACK
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=True)
        self.assertEqual(ani, animations.Action.ATTACK)

        # idle and throw
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.THROW
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=True)
        self.assertEqual(ani, animations.Action.THROW)

        # idle without an action
        state.delta.x = 0
        state.delta.y = 0
        state.action = binding.Action.NONE
        ani = state.get_next_animation(is_on_ladder=False, is_on_platform=True)
        self.assertEqual(ani, animations.Action.IDLE)

    # ------------------------------------------------------------------------------------------------------------------

    def test__verify_animation__cannot_interrupt_blocking(self):
        state = binding.InputState()
        phys_actor = physics.Actor(object_id=1, pos=pygame.math.Vector2())

        # traverse each combination of old and new action
        for old_action in animations.Action:
            for new_action in animations.Action:
                result = state.verify_animation(phys_actor, old_action, new_action)
                if old_action in animations.BLOCKING_ANIMATIONS:
                    # is blocked
                    self.assertIsNone(result)
                else:
                    # is accepted
                    self.assertEqual(result, new_action)

    def test__verify_animation__cannot_jump_in_air(self):
        state = binding.InputState()
        phys_actor = physics.Actor(object_id=1, pos=pygame.math.Vector2())

        state.delta.x = 1.0
        state.delta.y = 1.0
        result = state.verify_animation(phys_actor, animations.Action.JUMP, animations.Action.JUMP)

        self.assertEqual(result, animations.Action.JUMP)
        self.assertEqual(state.delta.y, 0.0)

    def test__verify_animation__can_change_direction_in_air(self):
        state = binding.InputState()
        phys_actor = physics.Actor(object_id=1, pos=pygame.math.Vector2())

        state.delta.x = 1.0
        result = state.verify_animation(phys_actor, animations.Action.JUMP, animations.Action.JUMP)

        self.assertEqual(result, animations.Action.JUMP)
        self.assertEqual(state.delta.x, 1.0)
