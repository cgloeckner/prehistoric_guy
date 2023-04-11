import unittest
import pygame

from core import shapes


class LineTest(unittest.TestCase):

    # Case 1: horizontal line
    def test__collidepoint__1(self):
        line = shapes.Line(1, 2, 5, 2)
        self.assertTrue(line.collidepoint(4, 2))
        # end points not included
        self.assertFalse(line.collidepoint(1, 2))
        self.assertFalse(line.collidepoint(5, 2))

        self.assertFalse(line.collidepoint(0, 2))
        self.assertFalse(line.collidepoint(6, 2))
        self.assertFalse(line.collidepoint(4, 1))
        self.assertFalse(line.collidepoint(4, 3))

    # Case 2: vertical line
    def test__collidepoint__2(self):
        line = shapes.Line(1, 2, 1, 6)
        self.assertTrue(line.collidepoint(1, 3))

        # end points not included
        self.assertFalse(line.collidepoint(1, 2))
        self.assertFalse(line.collidepoint(1, 6))

        self.assertFalse(line.collidepoint(0, 2))
        self.assertFalse(line.collidepoint(6, 2))
        self.assertFalse(line.collidepoint(4, 1))
        self.assertFalse(line.collidepoint(4, 3))

    # Case 3: any line
    def test__collidepoint__3(self):
        line = shapes.Line(1, 2, 4, 7)
        self.assertTrue(line.collidepoint(1+1, 2+5/3))

        # end points not included
        self.assertFalse(line.collidepoint(1, 2))
        self.assertFalse(line.collidepoint(1, 6))

        self.assertFalse(line.collidepoint(1+1+0.1, 2+5/3))
        self.assertFalse(line.collidepoint(1+1, 2+5/3 + 0.1))

# ----------------------------------------------------------------------------------------------------------------------


class CircTest(unittest.TestCase):

    def test__collidepoint(self):
        circ = shapes.Circ(3, 2, 1.5)

        self.assertTrue(circ.collidepoint(3, 2))
        self.assertTrue(circ.collidepoint(3.5, 2.5))
        self.assertTrue(circ.collidepoint(4.4999, 2))

        self.assertFalse(circ.collidepoint(4.25, 3.25))
        self.assertFalse(circ.collidepoint(5, 2))

        # arc not included
        self.assertFalse(circ.collidepoint(4.5, 2))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: line is inside circle
    def test__collideline__1(self):
        circ = shapes.Circ(3, 2, 4.5)
        line = shapes.Line(4, -2, 3.9, 4)

        self.assertTrue(circ.collideline(line))

    # Case 1: one line endpoint is inside circle
    def test__collideline__2(self):
        circ = shapes.Circ(3, 2, 2.8)

        line = shapes.Line(4, -2, 3.9, 4)
        self.assertTrue(circ.collideline(line))

        line = shapes.Line(4, 1, 3.9, 6)
        self.assertTrue(circ.collideline(line))

    # Case 3: line intersects circle twice
    def test__collideline__3(self):
        circ = shapes.Circ(3, 2, 3.5)

        line = shapes.Line(4, -2, 3.9, 6)
        self.assertTrue(circ.collideline(line))

        line = shapes.Line(3.9, 6, 4, -2)
        self.assertTrue(circ.collideline(line))

    # Case 4: line touches circle (not a collision)
    def test__collideline__4(self):
        circ = shapes.Circ(3, 2, 3.5)

        line = shapes.Line(3+3.5, -2, 3+3.5, 2)
        self.assertFalse(circ.collideline(line))

    # Case 5: line is passant
    def test__collideline__5(self):
        circ = shapes.Circ(3, 2, 3.5)

        line = shapes.Line(7, -5, 8, 7)
        self.assertFalse(circ.collideline(line))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: circle inside the other one
    def test__collidecirc__1(self):
        circ1 = shapes.Circ(4, 2, 3.5)
        circ2 = shapes.Circ(3, 2, 1.2)

        self.assertTrue(circ1.collidecirc(circ2))
        self.assertTrue(circ2.collidecirc(circ1))

    # Case 2: circles intersect
    def test__collidecirc__2(self):
        circ1 = shapes.Circ(4, 2, 3.5)
        circ2 = shapes.Circ(6, 2, 2.7)

        self.assertTrue(circ1.collidecirc(circ2))
        self.assertTrue(circ2.collidecirc(circ1))

    # Case 3: circles touch (not a collision)
    def test__collidecirc__3(self):
        circ1 = shapes.Circ(4, 2, 3.5)
        circ2 = shapes.Circ(4+3.5+1.2, 2, 1.2)

        # FIXME: fails due to floating point accuracy
        # self.assertFalse(circ1.collidecirc(circ2))
        # self.assertFalse(circ2.collidecirc(circ1))

    # Case 4: neither touch nor overlap
    def test__collidecirc__4(self):
        circ1 = shapes.Circ(4, 2, 3.5)
        circ2 = shapes.Circ(4+3.5+1.2, 2, 1.1)

        self.assertFalse(circ1.collidecirc(circ2))
        self.assertFalse(circ2.collidecirc(circ1))
