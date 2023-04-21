import unittest
from dataclasses import dataclass

from core import objectids


@dataclass
class Demo:
    object_id: int
    value: str


class ObjectIdTest(unittest.TestCase):

    def test__object_id_generator(self):
        gen = objectids.object_id_generator()
        self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 2)
        self.assertEqual(next(gen), 3)

    def test__get_by_id(self):
        lis = objectids.IdList[Demo]()
        lis.append(Demo(1, 'first'))
        lis.append(Demo(4, 'fourth'))
        lis.append(Demo(7, 'seventh'))

        el = lis.get_by_id(4)
        self.assertEqual(id(el), id(lis[1]))

        el = lis.get_by_id(5)
        self.assertIsNone(el)
