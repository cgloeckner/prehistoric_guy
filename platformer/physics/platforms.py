import pygame
import math
from dataclasses import dataclass, field
from typing import Optional, Tuple, Callable, Sequence, List
from enum import IntEnum

from core import shapes


class HoverType(IntEnum):
    NONE = 0
    SIN = 1
    COS = 2


@dataclass
class Hovering:
    x: HoverType = HoverType.NONE
    y: HoverType = HoverType.NONE
    amplitude: float = 1.0

    index: int = 0
    delta: pygame.math.Vector2 = field(default_factory=pygame.math.Vector2)

    @staticmethod
    def get_hover_func(value: HoverType) -> Callable[[float], float]:
        if value == HoverType.SIN:
            return math.sin

        if value == HoverType.COS:
            return math.cos

        return lambda x: 0.0

    def does_move(self) -> bool:
        return self.x != HoverType.NONE or self.y != HoverType.NONE

    def update(self, elapsed_ms: int) -> None:
        """Updates the hovering information and yields by how much hovering is caused."""
        # calculate movement delta
        self.index += 1
        angle = 2 * math.pi * self.index / 360.0

        self.delta = pygame.math.Vector2()
        self.delta.x = self.get_hover_func(self.x)(angle) * elapsed_ms / 1000.0
        self.delta.y = self.get_hover_func(self.y)(angle) * elapsed_ms / 1000.0

        self.delta *= self.amplitude


@dataclass
class Platform:
    pos: pygame.math.Vector2  # bottom left
    width: int
    height: int = 0
    hover: Hovering = field(default_factory=Hovering)

    def get_line(self) -> shapes.Line:
        """Returns the platform's top edge."""
        y_top = self.pos.y + self.height
        return shapes.Line(self.pos.x, y_top, self.pos.x + self.width, y_top)

    def contains_point(self, pos: pygame.math.Vector2) -> bool:
        """Test whether the position is inside the platform. Inside includes all edges except for the top edge.
        Returns True if the point is inside unless the at top edge.
        """
        if self.pos.y + self.height == pos.y:
            # exclude top edge
            return False

        return self.pos.x <= pos.x <= self.pos.x + self.width and self.pos.y <= pos.y < self.pos.y + self.height

    def supports_point(self, pos: pygame.math.Vector2) -> bool:
        """Tests if the pos is on the platform's top edge or not."""
        line = self.get_line()
        return line.collidepoint(pos.x, pos.y)

    def was_traverse_from_above(self, start_point: pygame.math.Vector2, end_point: pygame.math.Vector2) -> bool:
        """Test whether the move from start_point to end_point went through the top of the platform."""
        # NOTE: cannot use regular line intersection, because jumping up through a platform is no collision
        line = self.get_line()
        y_top = self.pos.y + self.height
        return end_point.y < y_top <= start_point.y and (line.a.x < start_point.x < line.b.x or
                                                         line.a.x < end_point.x < line.b.x)

    def get_landing_point(self, start_point: pygame.math.Vector2, end_point: pygame.math.Vector2) \
            -> Optional[pygame.math.Vector2]:
        """Returns the intersection point between the line from start_point to end_point and the platform's top edge.
        """
        y_top = self.pos.y + self.height
        top = shapes.Line(self.pos.x, y_top, self.pos.x + self.width, y_top)
        motion = shapes.Line(*start_point, *end_point)
        return top.collideline(motion)


# FIXME: This is not required anymore
def get_platform_collision(pos: pygame.math.Vector2, platform_seq: Sequence[Platform]) -> Optional[Platform]:
    """Returns the next-best platform from the list that contains the given position, or None."""
    for platform in platform_seq:
        if platform.contains_point(pos):
            return platform
    return None


def get_landing_platform(start_point: pygame.math.Vector2, end_point: pygame.math.Vector2,
                         platform_seq: Sequence[Platform]) -> Optional[Platform]:
    """Returns the closest platform that was traversed from above, or None.
    The approximated traversal collision point is used as a metric to get the closest platform but not returned.
    """
    if start_point.y == end_point.y:
        return None

    relevant: List[Tuple[Platform, float]] = list()
    for platform in platform_seq:
        if not platform.was_traverse_from_above(start_point, end_point):
            continue

        # calculate y-distance between position and platform, because platforms are always vertically
        distance = abs(start_point.y - platform.pos.y)
        relevant.append((platform, distance))

    if len(relevant) == 0:
        return None

    return min(relevant, key=lambda tup: tup[1])[0]


def get_support_platform(pos: pygame.math.Vector2, platform_seq: Sequence[Platform]) -> Optional[Platform]:
    """Returns any platform whose top edges the point is located, or None."""
    for platform in platform_seq:
        if platform.supports_point(pos):
            return platform

    return None
