import pygame
from dataclasses import dataclass, field
from enum import IntEnum


GRAVITY: float = 9.81
MAX_FALLING_SPEED: float = -5.0

MOVE_SPEED_FACTOR: float = 4.0


class FaceDirection(IntEnum):
    LEFT = -1
    RIGHT = 1


@dataclass
class MovementData:
    speed: float = 1.0
    face_x: FaceDirection = FaceDirection.RIGHT
    force: pygame.math.Vector2 = field(default_factory=pygame.math.Vector2)

    def get_jump_height_difference(self, elapsed_ms: int) -> float:
        """Calculates falling distances using f(x) = a * t^2.
        Returns the secant growth within a few elapsed_ms.
        """
        arg1 = arg2 = self.force.y
        arg2 += elapsed_ms / 2000.0  # FIXME to make more clear what's happening here

        old_h = GRAVITY * arg1 ** 2
        new_h = GRAVITY * arg2 ** 2
        return new_h - old_h

    def apply_gravity(self, elapsed_ms: int) -> bool:
        """Alters the given position's y-coordinate by simulating gravity.
        Returns True if the object suddenly starts falling, else False.
        """
        if self.force.y == 0.0:
            # start falling
            self.force.y = -1.0
            return True

        old_force_y = self.force.y
        self.force.y -= 3.0 * elapsed_ms / 1000.0

        if self.force.y == 0.0:
            self.force.y -= 0.001
            return True

        if self.force.y < MAX_FALLING_SPEED:
            self.force.y = MAX_FALLING_SPEED

        return self.force.y < 0 < old_force_y

    def apply_movement(self, pos: pygame.math.Vector2, elapsed_ms: int, is_on_ladder: bool = False) \
            -> pygame.math.Vector2:
        """Applies the force to the given position vector in place. This updates the facing direction as well.
        FIXME: write about gravity- vs. ladder forcey
        Returns a copy of the old position before the in-place change happened.
        """
        if self.force.x > 0.0:
            self.face_x = FaceDirection.RIGHT
        elif self.force.x < 0.0:
            self.face_x = FaceDirection.LEFT

        old_pos = pos.copy()
        pos.x += self.force.x * self.speed * MOVE_SPEED_FACTOR * elapsed_ms / 1000.0

        if is_on_ladder:
            pos.y += self.force.y * self.speed * MOVE_SPEED_FACTOR * elapsed_ms / 1000.0

        elif self.force.y != 0.0:
            delta_y = self.get_jump_height_difference(elapsed_ms)
            pos.y += delta_y

        return old_pos
