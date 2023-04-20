import unittest

from core import bounded_value


class BoundedValueTest(unittest.TestCase):

    def test__modify(self):
        container = bounded_value.Int(5, 10)
        self.assertEqual(container.value, 5)
        self.assertEqual(container.max_value, 10)

        container.value = 7
        self.assertEqual(container.value, 7)
        self.assertEqual(container.max_value, 10)

        container.value += 2
        self.assertEqual(container.value, 9)
        self.assertEqual(container.max_value, 10)

        # cannot exceed max
        container.value += 2
        self.assertEqual(container.value, 10)
        self.assertEqual(container.max_value, 10)

        container.value -= 7
        self.assertEqual(container.value, 3)
        self.assertEqual(container.max_value, 10)

        # cannot exceed 0
        container.value -= 7
        self.assertEqual(container.value, 0)
        self.assertEqual(container.max_value, 10)

        # add number
        container = container + 2
        self.assertEqual(container.value, 2)
        self.assertEqual(container.max_value, 10)

        # add number never exceeds
        container = container + 12
        self.assertEqual(container.value, 10)
        self.assertEqual(container.max_value, 10)

        # iadd number
        container.value = 1
        container += 3
        self.assertEqual(container.value, 4)
        self.assertEqual(container.max_value, 10)

        # iadd number never exceeds
        container += 12
        self.assertEqual(container.value, 10)
        self.assertEqual(container.max_value, 10)

        # sub number
        container.value = 5
        container = container - 2
        self.assertEqual(container.value, 3)
        self.assertEqual(container.max_value, 10)

        # sub number never exceeds
        container = container - 4
        self.assertEqual(container.value, 0)
        self.assertEqual(container.max_value, 10)

        # isub number
        container.value = 3
        container -= 2
        self.assertEqual(container.value, 1)
        self.assertEqual(container.max_value, 10)

        # isub number never exceeds
        container -= 2
        self.assertEqual(container.value, 0)
        self.assertEqual(container.max_value, 10)

        # comparision
        container.value = 4
        self.assertTrue(container == 4)
        self.assertFalse(container != 4)
        self.assertTrue(container < 5)
        self.assertTrue(container <= 5)
        self.assertTrue(container > 3)
        self.assertTrue(container >= 3)
