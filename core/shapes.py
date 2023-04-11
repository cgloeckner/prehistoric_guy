import pygame
from typing import Tuple, Optional

VECTOR_TUPLE = Tuple[float, float]


class Line:
    def __init__(self, pos1: VECTOR_TUPLE, pos2: VECTOR_TUPLE):
        self.a = pygame.math.Vector2(pos1)
        self.b = pygame.math.Vector2(pos2)

    def collidepoint(self, pos: Tuple[float, float], tolerance: float = 0.01) -> bool:
        """The corresponding linear equations system's solution is calculated. If both line arguments r and s are
        close enough (see tolerance), the point is inside the line.
        Returns True if the pos lies inside the line except for the end points.
        """
        pos = pygame.math.Vector2(pos)
        print('test', self.a, self.b)

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
    def __init__(self, center: VECTOR_TUPLE, radius: float):
        self.center = pygame.math.Vector2(center)
        self.radius = radius

    def collidepoint(self, pos: VECTOR_TUPLE) -> bool:
        """Points on the arc of the circle are excepted.
        Returns True if the position lies within the radius.
        """
        distance = self.center.distance_squared_to(pygame.math.Vector2(pos))
        return distance < self.radius ** 2

    def collideline(self, line: Line) -> bool:
        """Tests for line intersection between the given line and the circle's radius (using both normals vectors).
        Returns True if this line intersects the given line except for an intersection on the circle's edge
        """
        if self.collidepoint(tuple(line.a)) or self.collidepoint(tuple(line.b)):
            return True

        for sign in [1, -1]:
            normal = line.b - line.a
            normal.x, normal.y = normal.y, normal.x
            normal = normal.normalize() * self.radius
            endpoint = self.center + sign * normal

            test_point = line.collideline(Line(tuple(self.center), tuple(endpoint)))
            if test_point is not None:
                # makes sure that the lines' intersection is inside the circle (not on the edge)
                return self.collidepoint(tuple(test_point))

        return False

    def collidecirc(self, other: 'Circ') -> bool:
        """Calculates the distance between the centers. Two circles touch do not mean collision.
        Returns True if that distance is within the added radii."""
        distance = self.center.distance_squared_to(other.center)
        return distance < (self.radius + other.radius) ** 2

    def colliderect(self, rect: pygame.Rect) -> bool:
        """If the circle's center is not within the rect, all edges are tested for line-circle-intersection.
        """
        if rect.collidepoint(self.center):
            return True

        for edge in ((rect.topleft, rect.topright), (rect.topright, rect.bottomright),
                     (rect.bottomright, rect.bottomleft), (rect.bottomleft, rect.topleft)):
            if self.collideline(Line(*edge)):
                return True

        return False
