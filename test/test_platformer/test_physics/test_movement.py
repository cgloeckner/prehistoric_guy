import unittest
import pygame

from platformer.physics import movement


class MovementPhysicsTest(unittest.TestCase):

    def test__jump_height_difference(self):
        data = movement.MovementData()
        data.force.y = -1.0

        delta1 = data.get_jump_height_difference(10)
        delta2 = data.get_jump_height_difference(20)
        self.assertLess(delta1, 0)
        self.assertLess(delta2, delta1)

        data.force.y = 0.5

        delta1 = data.get_jump_height_difference(10)
        delta2 = data.get_jump_height_difference(20)
        self.assertGreater(delta1, 0)
        self.assertGreater(delta2, delta1)

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
        data.force.y = 0.00001
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
        old_pos = data.apply_movement(pos, 10)
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
