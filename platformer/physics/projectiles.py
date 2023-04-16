import pygame
from dataclasses import dataclass, field
from typing import Optional

from core.constants import ObjectType
from core import shapes

from platformer.physics.constants import *
from platformer.physics.movement import MovementData
from platformer.physics.actors import Actor
from platformer.physics.platforms import Platform


GRAVITY_WEIGHT: float = 0.1


@dataclass
class Projectile:
    pos: pygame.math.Vector2  # center
    radius: float = OBJECT_RADIUS
    object_type: ObjectType = ObjectType.WEAPON
    movement: MovementData = field(default_factory=MovementData)
    from_actor: Optional[Actor] = None

    def get_circ(self) -> shapes.Circ:
        """Returns the projectile's bounding circle."""
        return shapes.Circ(*self.pos, self.radius)

    def can_hit(self, actor: Actor) -> bool:
        return self.from_actor is None or self.from_actor != actor

    def land_on_platform(self, platform: Platform, old_pos: pygame.math.Vector2) -> None:
        """Handles landing on a platform by calculating a landing point, resetting the force vector and similar
        things."""
        landing_pos = platform.get_landing_point(old_pos, self.pos)
        if landing_pos is None:
            return

        self.pos = landing_pos.copy()
        self.movement.force = pygame.math.Vector2()

    def collide_with_platform(self, old_pos: pygame.math.Vector2) -> None:
        """Handles colliding with a platform by resetting the position, the force vector and similar things."""
        self.pos = old_pos.copy()
        self.movement.force = pygame.math.Vector2()
