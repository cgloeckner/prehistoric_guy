import unittest

from core import constants
from platformer.animations import actions, frames


class FrameAnimationTest(unittest.TestCase):

    def test__start(self):
        actor = frames.FrameAnimation()
        actor.frame_id = 2
        actor.duration_ms = 125
        actor.max_duration_ms = 600

        # start new animation
        actor.start(actions.Action.ATTACK)
        self.assertEqual(actor.action, actions.Action.ATTACK)
        self.assertEqual(actor.frame_id, 0)
        self.assertEqual(actor.duration_ms, frames.ANIMATION_FRAME_DURATION)
        self.assertEqual(actor.max_duration_ms, frames.ANIMATION_FRAME_DURATION)

        # trigger again before finished
        actor.frame_id = 2
        actor.duration_ms = 125
        actor.max_duration_ms = 600
        actor.total_frame_time_ms = 745
        actor.start(actions.Action.ATTACK)
        self.assertEqual(actor.action, actions.Action.ATTACK)
        self.assertEqual(actor.frame_id, 2)
        self.assertEqual(actor.duration_ms, 125)
        self.assertEqual(actor.max_duration_ms, 600)

        # custom duration
        actor.start(actions.Action.DIE, 235)
        self.assertEqual(actor.action, actions.Action.DIE)
        self.assertEqual(actor.frame_id, 0)
        self.assertEqual(actor.duration_ms, 235)
        self.assertEqual(actor.max_duration_ms, 235)

    def test__step_frame(self):
        actor = frames.FrameAnimation()
        actor.action = actions.Action.ATTACK
        actor.frame_id = 0
        actor.duration_ms = 200
        actor.max_duration_ms = 200

        # stays within frame
        finished = actor.step_frame(40)
        self.assertFalse(finished)
        self.assertEqual(actor.action, actions.Action.ATTACK)
        self.assertEqual(actor.frame_id,0)
        self.assertEqual(actor.duration_ms, 160)

        # go to next frame
        finished = actor.step_frame(240)
        self.assertFalse(finished)
        self.assertEqual(actor.action, actions.Action.ATTACK)
        self.assertEqual(actor.frame_id, 1)
        self.assertEqual(actor.duration_ms, 120)

        # skip frame on lag
        actor.frame_id = 0
        actor.duration_ms = 200
        finished = actor.step_frame(680)
        self.assertFalse(finished)
        self.assertEqual(actor.action, actions.Action.ATTACK)
        self.assertEqual(actor.frame_id, 3)
        self.assertEqual(actor.duration_ms, 120)

        # finish last frame
        actor.frame_id = constants.ANIMATION_NUM_FRAMES - 1
        actor.duration_ms = 5
        finished = actor.step_frame(10)
        self.assertTrue(finished)
        self.assertEqual(actor.frame_id, constants.ANIMATION_NUM_FRAMES)
        self.assertGreater(actor.duration_ms, 0)

    def test__handle_finish(self):
        # looped animations
        for action in actions.LOOPED_ANIMATIONS:
            actor = frames.FrameAnimation()
            actor.action = action
            actor.frame_id = constants.ANIMATION_NUM_FRAMES
            actor.handle_finish()
            self.assertEqual(actor.action, action)
            self.assertEqual(actor.frame_id, 0)

        # reset animations
        for action in actions.RESET_TO_IDLE_ANIMATIONS:
            actor = frames.FrameAnimation()
            actor.action = action
            actor.frame_id = constants.ANIMATION_NUM_FRAMES
            actor.handle_finish()
            self.assertEqual(actor.action, actions.Action.IDLE)
            self.assertEqual(actor.frame_id, 0)

        # climb resets to hold
        actor = frames.FrameAnimation()
        actor.action = actions.Action.CLIMB
        actor.frame_id = constants.ANIMATION_NUM_FRAMES
        actor.handle_finish()
        self.assertEqual(actor.action, actions.Action.HOLD)
        self.assertEqual(actor.frame_id, 0)

        # freeze animations
        for action in actions.FREEZE_AT_END_ANIMATIONS:
            actor = frames.FrameAnimation()
            actor.action = action
            actor.frame_id = constants.ANIMATION_NUM_FRAMES
            actor.handle_finish()
            self.assertEqual(actor.action, action)
            self.assertEqual(actor.frame_id, constants.ANIMATION_NUM_FRAMES-1)
