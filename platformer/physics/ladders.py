import pygame
from dataclasses import dataclass
from typing import Sequence, Tuple, Optional, List

from core import shapes

from platformer.physics.constants import *


@dataclass
class Ladder:
    pos: pygame.math.Vector2  # bottom left
    height: int

    def get_line(self) -> shapes.Line:
        """Returns the ladder's vertical (mid) line."""
        return shapes.Line(*self.pos, self.pos.x, self.pos.y + self.height)

    def is_in_reach_of(self, pos: pygame.math.Vector2) -> bool:
        """Test whether the position is in reach of the ladder.
        The ladder is in reach +/- OBJECT_RADIUS in x-wise.
        The ladder's top and bottom are in reach y-wise.
        """
        return self.pos.x - OBJECT_RADIUS <= pos.x <= self.pos.x + OBJECT_RADIUS and \
            self.pos.y + OBJECT_RADIUS <= pos.y <= self.pos.y + self.height


def get_closest_ladder_in_reach(pos: pygame.math.Vector2, ladder_seq: Sequence[Ladder]) -> Optional[Ladder]:
    """Returns the closest ladder in reach.
    """
    relevant: List[Tuple[Ladder, float]] = list()
    for ladder in ladder_seq:
        if not ladder.is_in_reach_of(pos):
            continue

        # calculate x-distance between position and ladder, because ladders are always vertically
        distance = abs(pos.x - ladder.pos.x)
        relevant.append((ladder, distance))

    if len(relevant) == 0:
        return None

    return min(relevant, key=lambda tup: tup[1])[0]
