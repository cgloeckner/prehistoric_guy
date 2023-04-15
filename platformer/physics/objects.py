import pygame
from dataclasses import dataclass

from core.constants import ObjectType
from core import shapes

from platformer.physics.constants import *


@dataclass
class Object:
    pos: pygame.math.Vector2  # center
    object_type: ObjectType

    def get_circ(self) -> shapes.Circ:
        """Returns the object's bounding circle."""
        return shapes.Circ(*self.pos, OBJECT_RADIUS)
