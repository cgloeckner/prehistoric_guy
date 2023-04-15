import pygame
from dataclasses import dataclass, field
from typing import Optional

from core.constants import ObjectType
from core import shapes

from platformer.physics.constants import *
from platformer.physics.movement import MovementData
from platformer.physics.actors import Actor


@dataclass
class Projectile:
    pos: pygame.math.Vector2  # center
    radius: float

    movement: MovementData = field(default_factory=MovementData)

    object_type: ObjectType = ObjectType.WEAPON
    # FIXME: not implemented yet: spin_speed: float = PROJECTILE_SPIN
    origin: Optional[Actor] = None

    def get_circ(self) -> shapes.Circ:
        """Returns the projectile's bounding circle."""
        return shapes.Circ(*self.pos, self.radius)



    def can_hit(self, actor: Actor) -> bool:
        return self.origin is None or self.origin != actor
