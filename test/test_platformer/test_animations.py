import unittest

from core import constants, resources

from platformer import animations


class AnimationFunctionsTest(unittest.TestCase):

    # Case 1: Can change animation
    def test__start__1(self):
        actor = animations.Actor(13)
        actor.frame_id = 2
        actor.frame_duration_ms = 125
        actor.frame_max_duration_ms = 600
        actor.total_frame_time_ms = 745

        animations.start(actor, animations.Action.ATTACK)
        self.assertEqual(actor.action, animations.Action.ATTACK)
        self.assertEqual(actor.frame_id, 0)
        self.assertEqual(actor.frame_duration_ms, animations.ANIMATION_FRAME_DURATION)
        self.assertEqual(actor.frame_max_duration_ms, animations.ANIMATION_FRAME_DURATION)
        self.assertEqual(actor.total_frame_time_ms, 0)

    # Case 2: Can't change to the same animation
    def test__start__2(self):
        actor = animations.Actor(13)
        actor.action = animations.Action.ATTACK
        actor.frame_id = 2
        actor.frame_duration_ms = 125
        actor.frame_max_duration_ms = 600
        actor.total_frame_time_ms = 745

        animations.start(actor, animations.Action.ATTACK)
        self.assertEqual(actor.action, animations.Action.ATTACK)
        self.assertEqual(actor.frame_id, 2)
        self.assertEqual(actor.frame_duration_ms, 125)
        self.assertEqual(actor.frame_max_duration_ms, 600)
        self.assertEqual(actor.total_frame_time_ms, 745)

    # Case 3: Optional duration
    def test__start__3(self):
        actor = animations.Actor(13)
        actor.frame_id = 2
        actor.frame_duration_ms = 125
        actor.frame_max_duration_ms = 600
        actor.total_frame_time_ms = 745

        animations.start(actor, animations.Action.ATTACK, 235)
        self.assertEqual(actor.action, animations.Action.ATTACK)
        self.assertEqual(actor.frame_id, 0)
        self.assertEqual(actor.frame_duration_ms, 235)
        self.assertEqual(actor.frame_max_duration_ms, 235)
        self.assertEqual(actor.total_frame_time_ms, 0)


# ----------------------------------------------------------------------------------------------------------------------

class AnimatingSystemTest(unittest.TestCase):

    def setUp(self):
        class DemoListener(animations.EventListener):
            def __init__(self):
                self.last = None

            def on_step(self, ani: animations.Actor) -> None:
                self.last = ('step', ani)

            def on_climb(self, ani: animations.Actor) -> None:
                self.last = ('climb', ani)

            def on_attack(self, ani: animations.Actor) -> None:
                self.last = ('attack', ani)

            def on_throw(self, ani: animations.Actor) -> None:
                self.last = ('throw', ani)

            def on_died(self, ani: animations.Actor) -> None:
                self.last = ('died', ani)

        self.listener = DemoListener()
        self.ctx = animations.Context()
        self.sys = animations.Animating(self.listener, self.ctx)

        self.actor = animations.Actor(45)
        self.ctx.actors.append(self.actor)

        animations.start(self.actor, animations.Action.ATTACK, 300)
        self.actor.frame_duration_ms = 200
        self.actor.total_frame_time_ms = 100
        self.actor.frame_id = 1

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: get existing actor
    def test__get_by_id__1(self):
        got = self.sys.get_actor_by_id(45)

        self.assertEqual(id(self.actor), id(got))

    # Case 2: cannot get non-existing actor
    def test__get_by_id__2(self):
        with self.assertRaises(IndexError):
            self.sys.get_actor_by_id(23)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: notify on_step
    def test__notify__animation__1(self):
        self.actor.action = animations.Action.MOVE
        self.sys.notify_animation(self.actor)

        self.assertIsNotNone(self.listener.last)
        self.assertEqual(self.listener.last[0], 'step')
        self.assertEqual(self.listener.last[1].object_id, self.actor.object_id)

    # Case 2: notify on_attack
    def test__notify__animation__2(self):
        self.actor.action = animations.Action.ATTACK
        self.sys.notify_animation(self.actor)

        self.assertIsNotNone(self.listener.last)
        self.assertEqual(self.listener.last[0], 'attack')
        self.assertEqual(self.listener.last[1].object_id, self.actor.object_id)

    # Case 3: notify throw
    def test__notify__animation__3(self):
        self.actor.action = animations.Action.THROW
        self.sys.notify_animation(self.actor)

        self.assertIsNotNone(self.listener.last)
        self.assertEqual(self.listener.last[0], 'throw')
        self.assertEqual(self.listener.last[1].object_id, self.actor.object_id)

    # Case 4: notify died
    def test__notify__animation__4(self):
        self.actor.action = animations.Action.DIE
        self.sys.notify_animation(self.actor)

        self.assertIsNotNone(self.listener.last)
        self.assertEqual(self.listener.last[0], 'died')
        self.assertEqual(self.listener.last[1].object_id, self.actor.object_id)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: update but keep within frame
    def test__update_frame__1(self):
        self.sys.update_frame(self.actor, 40)

        self.assertEqual(self.actor.frame_duration_ms, 160)
        self.assertEqual(self.actor.frame_id, 1)
        self.assertEqual(self.actor.action, animations.Action.ATTACK)

    # Case 2: update and go to next frame
    def test__update_frame__2(self):
        self.sys.update_frame(self.actor, 240)

        self.assertEqual(self.actor.frame_duration_ms, 260)
        self.assertEqual(self.actor.frame_id, 2)
        self.assertEqual(self.actor.action, animations.Action.ATTACK)

    # Case 3: update and go to next frame
    def test__update_frame__3(self):
        self.actor.frame_id = constants.ANIMATION_NUM_FRAMES - 1
        self.sys.update_frame(self.actor, 220)

        self.assertEqual(self.actor.frame_duration_ms, 280)
        self.assertEqual(self.actor.frame_id, 0)
        self.assertEqual(self.actor.action, animations.Action.IDLE)

        self.assertEqual(self.listener.last[0], 'attack')

    # Case 4: does skip animation frames after delay
    def test__update_frame__4(self):
        self.sys.update_frame(self.actor, 680)

        self.assertEqual(self.actor.frame_duration_ms, 120)
        self.assertEqual(self.actor.frame_id, 3)
        self.assertEqual(self.actor.action, animations.Action.ATTACK)

    # Case 5: some animations are looped
    def test__update_frame__5(self):
        for action in animations.LOOPED_ANIMATIONS:
            self.actor.action = action
            self.actor.frame_id = constants.ANIMATION_NUM_FRAMES - 1
            self.actor.frame_duration_ms = 5
            self.sys.update_frame(self.actor, 10)

            self.assertEqual(self.actor.frame_duration_ms, 295)
            self.assertEqual(self.actor.frame_id, 0)
            self.assertEqual(self.actor.action, action)

    # Case 6: some animations reset to idle
    def test__update_frame__6(self):
        for action in animations.RESET_TO_IDLE_ANIMATIONS:
            self.actor.action = action
            self.actor.frame_id = constants.ANIMATION_NUM_FRAMES - 1
            self.actor.frame_duration_ms = 5
            self.sys.update_frame(self.actor, 10)

            self.assertEqual(self.actor.frame_duration_ms, 295)
            self.assertEqual(self.actor.frame_id, 0)
            self.assertEqual(self.actor.action, animations.Action.IDLE)

    # Case 7: climbing leads to holding
    def test__update_frame__7(self):
        self.actor.action = animations.Action.CLIMB
        self.actor.frame_id = constants.ANIMATION_NUM_FRAMES - 1
        self.actor.frame_duration_ms = 5
        self.sys.update_frame(self.actor, 10)

        self.assertEqual(self.actor.frame_duration_ms, 295)
        self.assertEqual(self.actor.frame_id, 0)
        self.assertEqual(self.actor.action, animations.Action.HOLD)

    # Case 8: some animations freeze in the last frame
    def test__update_frame__8(self):
        for action in animations.FREEZE_AT_END_ANIMATIONS:
            self.actor.action = action
            self.actor.frame_id = constants.ANIMATION_NUM_FRAMES - 1
            self.actor.frame_duration_ms = 5
            self.sys.update_frame(self.actor, 10)

            self.assertEqual(self.actor.frame_duration_ms, 295)
            self.assertEqual(self.actor.frame_id, constants.ANIMATION_NUM_FRAMES-1)
            self.assertEqual(self.actor.action, action)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: y-offset is not used for most animations
    def test__update_movement__1(self):
        for _, action in animations.Action.__members__.items():
            if action in [animations.Action.MOVE, animations.Action.CLIMB]:
                continue

            self.actor.action = action
            self.actor.total_frame_time_ms = 5
            self.sys.update_movement(self.actor, 10)

            self.assertEqual(self.actor.total_frame_time_ms, 0)
            self.assertAlmostEqual(self.actor.delta_y, 0.0)

    # Case 2: y-offset is calculated for movement and climbing, and never gets too large
    def test__update_movement__2(self):
        for action in [animations.Action.MOVE, animations.Action.CLIMB]:
            self.actor.action = action
            self.actor.total_frame_time_ms = 5
            self.sys.update_movement(self.actor, 10)

            for i in range(2000):
                self.assertEqual(self.actor.total_frame_time_ms, 15)
                self.assertLess(abs(self.actor.delta_y), 0.3)

    # ------------------------------------------------------------------------------------------------------------------

    def test__update(self):
        self.actor.action = animations.Action.MOVE
        self.sys.update(210)

        self.assertEqual(self.actor.frame_id, 2)
        self.assertAlmostEqual(self.actor.delta_y, -0.766, 2)
