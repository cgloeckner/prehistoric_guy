import pygame
from dataclasses import dataclass, field
from typing import Optional, Sequence, List

from core import shapes

from platformer.physics.ladders import Ladder
from platformer.physics.platforms import Platform
from platformer.physics.movement import MovementData, FaceDirection


@dataclass
class Actor:
    object_id: int
    pos: pygame.math.Vector2  # bottom center
    radius: float = 0.5
    movement: MovementData = field(default_factory=MovementData)

    at_ladder: Optional[Ladder] = None
    on_platform: Optional[Platform] = None

    def can_fall(self) -> bool:
        """Returns True if the actor is neither at a ladder nor on a platform, else False.
        """
        return self.at_ladder is None and self.on_platform is None

    def get_circ(self) -> shapes.Circ:
        """Returns the actor's bounding circle."""
        return shapes.Circ(*self.pos, self.radius)

    def can_fall(self) -> bool:
        return self.at_ladder is None and self.on_platform is None

    def get_all_faced_actors(self, actor_seq: Sequence['Actor'], max_distance: float) -> List['Actor']:
        """Searches the given sequence for actors who are within facing direction and range.
        Returns a list of all faced actors sorted by distance (closest first).
        """
        faced: List[Actor] = list()
        for other in actor_seq:
            if other == self:
                # cannot face himself
                continue

            if self.movement.face_x == FaceDirection.RIGHT and other.pos.x < self.pos.x:
                # looking into the wrong direction
                continue

            if self.movement.face_x == FaceDirection.LEFT and other.pos.x > self.pos.x:
                # looking into the wrong direction
                continue

            # calculate distance
            distance = self.pos.distance_squared_to(other.pos)
            if distance <= max_distance ** 2:
                faced.append(other)

        faced.sort(key=lambda o: self.pos.distance_squared_to(o.pos))
        return faced
