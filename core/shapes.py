import pygame
from typing import Tuple, Optional


class Line:
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.a = pygame.math.Vector2(x1, y1)
        self.b = pygame.math.Vector2(x2, y2)

    def collidepoint(self, x: float, y: float, tolerance: float = 0.01) -> bool:
        """The corresponding linear equations system's solution is calculated. If both line arguments r and s are
        close enough (see tolerance), the point is inside the line.
        Returns True if the pos lies inside the line except for the end points.
        """
        pos = pygame.math.Vector2(x, y)

        if self.a.x == self.b.x:
            # vertical line
            return self.a.x == pos.x and self.a.y < pos.y < self.b.y

        if self.a.y == self.b.y:
            # horizontal line
            return self.a.y == pos.y and self.a.x < pos.x < self.b.x

        # regular case
        r = (pos.x - self.a.x) / (self.b.x - self.a.x)
        if r <= 0 or r >= 1:
            return False

        y = self.a.y + r * (self.b.y - self.a.y)
        return abs(y - pos.y) < tolerance

    def collideline(self, other: 'Line') -> Optional[pygame.math.Vector2]:
        """The corresponding linear equations system's solution is calculated.
        Returns a Vector (x, y) for the intersection position or None.
        """
        x1, y1 = self.a
        x2, y2 = self.b
        x3, y3 = other.a
        x4, y4 = other.b

        denominator = x1 * (y3 - y4) - x2 * (y3 - y4) - (x3 - x4) * (y1 - y2)
        if denominator == 0:
            return

        numerator1 = x1 * (y3 - y4) - x3 * (y1 - y4) + x4 * (y1 - y3)
        numerator2 = -(x1 * (y2 - y3) - x2 * (y1 - y3) + x3 * (y1 - y2))
        mu1 = numerator1 / denominator
        mu2 = numerator2 / denominator

        if not 0 <= mu1 <= 1 or not 0 <= mu2 <= 1:
            return

        x = x1 + mu1 * (x2 - x1)
        y = y1 + mu1 * (y2 - y1)

        return pygame.math.Vector2(x, y)


class Circ:
    def __init__(self, x: float, y: float, radius: float):
        """
        :param x: center x
        :param y: center y
        :param radius: just the radius
        """
        self.center = pygame.math.Vector2(x, y)
        self.radius = radius

    def collidepoint(self, x: float, y: float) -> bool:
        """Points on the arc of the circle are excepted.
        Returns True if the position lies within the radius.
        """
        pos = pygame.math.Vector2(x, y)
        distance = self.center.distance_squared_to(pos)
        return distance < self.radius ** 2

    def collideline(self, line: Line) -> bool:
        """Tests for line intersection between the given line and the circle's radius (using both normals vectors).
        Returns True if this line intersects the given line except for an intersection on the circle's edge
        """
        if self.collidepoint(*line.a) or self.collidepoint(*line.b):
            return True

        for sign in [1, -1]:
            normal = line.b - line.a
            normal.x, normal.y = normal.y, normal.x
            normal = normal.normalize() * self.radius
            endpoint = self.center + sign * normal

            test_point = line.collideline(Line(*self.center, *endpoint))
            if test_point is not None:
                # makes sure that the lines' intersection is inside the circle (not on the edge)
                return self.collidepoint(*test_point)

        return False

    def collidecirc(self, other: 'Circ') -> bool:
        """Calculates the distance between the centers. Two circles touching may mean collision (based on floating
        point accuracy)
        Returns True if that distance is within the added radii."""
        distance = self.center.distance_squared_to(other.center)
        return distance < (self.radius + other.radius) ** 2
