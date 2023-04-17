import pygame
from dataclasses import dataclass

from core import constants, shapes


@dataclass
class Object:
    pos: pygame.math.Vector2  # center
    object_type: constants.ObjectType

    def get_circ(self) -> shapes.Circ:
        """Returns the object's bounding circle."""
        return shapes.Circ(*self.pos, constants.OBJECT_RADIUS)
