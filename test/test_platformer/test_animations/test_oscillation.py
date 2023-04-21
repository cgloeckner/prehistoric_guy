import unittest

from platformer.animations import actions, oscillation


class OscillateAnimationTest(unittest.TestCase):

    def test__get_move_swing(self):
        actor = oscillation.OscillateAnimation()
        actor.total_time_ms = 35_136
        value = actor.get_move_swing()
        self.assertGreater(value, -oscillation.MOVEMENT_SWING)
        self.assertLess(value, oscillation.MOVEMENT_SWING)

    def test__get_climb_swing(self):
        actor = oscillation.OscillateAnimation()
        actor.total_time_ms = 35_136
        value = actor.get_climb_swing()
        self.assertGreater(value, 0)

    def update(self):
        for _, action in actions.Action.__members__.items():

            if action in [actions.Action.MOVE, actions.Action.CLIMB]:
                actor = oscillation.OscillateAnimation()
                # some actions trigger this
                for i in range(2000):
                    self.assertEqual(actor.total_time_ms, 15)
                    self.assertLess(abs(actor.delta_y), 0.3)

            else:
                # most of them don't
                actor = oscillation.OscillateAnimation()
                actor.total_time_ms = 5
                actor.update(action, 10)

                self.assertEqual(actor.total_time_ms, 0)
                self.assertAlmostEqual(actor.delta_y, 0.0)
