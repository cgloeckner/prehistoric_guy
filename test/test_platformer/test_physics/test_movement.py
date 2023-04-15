import unittest
import pygame

from platformer.physics import movement


class MovementPhysicsTest(unittest.TestCase):

    def test__get_gravity_growth_factor(self):
        for ms in (0, 10, 250, 15000):
            factor = movement.MovementData.get_gravity_growth_factor(ms)
            self.assertGreaterEqual(factor, movement.MIN_GRAVITY_EFFECT)
            self.assertLessEqual(factor, movement.MAX_GRAVITY_EFFECT)

    def test__apply_gravity(self):
        data = movement.MovementData()

        # free fall if no force provided
        self.assertTrue(data.apply_gravity(10))
        self.assertEqual(data.force.x, 0)
        self.assertLess(data.force.y, 0)

        # y-force gets more intense
        old_y_force = data.force.y
        self.assertFalse(data.apply_gravity(10))
        self.assertLess(data.force.y, old_y_force)

        # jumping works
        data.force.y = 2.0
        self.assertFalse(data.apply_gravity(10))
        self.assertLess(data.force.y, 2.0)
        self.assertGreater(data.force.y, 0.0)

        # y-force gets less intense
        old_y_force = data.force.y
        self.assertFalse(data.apply_gravity(10))
        self.assertLess(data.force.y, old_y_force)

        # until the highest point is reached
        data.force.y = movement.JUMP_TO_FALL_THRESHOLD
        self.assertTrue(data.apply_gravity(10))
        self.assertLess(data.force.y, 0.0)

    def test__apply_movement(self):
        data = movement.MovementData()

        # no force means no motion
        pos = pygame.math.Vector2(1, 3)
        data.apply_movement(pos, 250)
        self.assertEqual(data.face_x, movement.FaceDirection.RIGHT)
        self.assertAlmostEqual(pos.x, 1.0)
        self.assertAlmostEqual(pos.y, 3.0)

        # regular case
        data.force.x = 1.0
        data.force.y = -0.5
        data.face_x = movement.FaceDirection.LEFT
        old_pos = pos.copy()
        data.apply_movement(pos, 10)
        self.assertEqual(data.face_x, movement.FaceDirection.RIGHT)
        self.assertGreater(pos.x, 1.0)
        self.assertLess(pos.y, 3.0)

        # in case of a lag, reverse direction
        delta = pos - old_pos
        pos = pygame.math.Vector2(1, 3)
        data.force.x = -1.0
        data.apply_movement(pos, 250)
        new_delta = pos - old_pos
        self.assertEqual(data.face_x, movement.FaceDirection.LEFT)
        self.assertLess(new_delta.x, -delta.x)
        self.assertLess(new_delta.y, delta.y)
