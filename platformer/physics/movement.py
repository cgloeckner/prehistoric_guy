import pygame
from dataclasses import dataclass, field
from enum import IntEnum


GRAVITY: float = 9.81
JUMP_SPEED_FACTOR: float = 0.5
JUMP_DURATION: int = 500

GRAVITY_EFFECT_ON_FORCE_VECTOR_PERCENT: float = 2.0
MIN_GRAVITY_EFFECT: float = 4.5
MAX_GRAVITY_EFFECT: float = 4.5
JUMP_TO_FALL_THRESHOLD: float = 0.5
MAX_FALLING_SPEED: float = -0.5

MOVE_SPEED_FACTOR: float = 4.0


class FaceDirection(IntEnum):
    LEFT = -1
    RIGHT = 1


@dataclass
class MovementData:
    speed: float = 1.0
    face_x: FaceDirection = FaceDirection.RIGHT
    force: pygame.math.Vector2 = field(default_factory=pygame.math.Vector2)
    jump_ms: int = 0  # duration of jump/fall

    @staticmethod
    def get_gravity_growth_factor(elapsed_ms) -> float:
        """This is"""
        factor = 1 + GRAVITY_EFFECT_ON_FORCE_VECTOR_PERCENT * elapsed_ms / 1000.0
        return pygame.math.clamp(factor, MIN_GRAVITY_EFFECT, MAX_GRAVITY_EFFECT)

    def get_jump_height_difference(self, elapsed_ms: int) -> float:
        """Calculates falling distances using
        #f(x) = -a * t ^ 2 + a * 0.25
        but flipping signs of x and y, hence
        #f(x) = 9 * t^2
        """
        arg1 = arg2 = self.force.y
        arg2 += elapsed_ms / 2000.0

        def f(x):
            return GRAVITY * x ** 2

        old_h = f(arg1)
        new_h = f(arg2)
        return (new_h - old_h)

    # @staticmethod
    # def get_jump_height_difference(elapsed_ms: int, delta_ms: int) -> float:
    #    """Calculates falling distances using
    #    f(x) = -a * (t - 0.5s) ^ 2 + a * 0.25
    #    where a full jump lasts 1s
    #    """
    #
    #    def f(x):
    #        return -GRAVITY * (x / JUMP_DURATION - 0.5) ** 2 + GRAVITY * 0.25
    #
    #    # cap maximum falling speed
    #    if elapsed_ms > 2000:
    #        elapsed_ms = 2000
    #
    #    old_h = f(elapsed_ms)
    #    new_h = f(elapsed_ms + delta_ms)
    #    return new_h - old_h

    def apply_gravity(self, pos: pygame.math.Vector2, elapsed_ms: int) -> bool:
        """Alters the given position's y-coordinate by simulating gravity. If the object suddenly starts falling,
        True is returned else False.
        """
        #if self.force.y == 0.0:
        #    return False
        #
        #delta_h = MovementData.get_jump_height_difference(self.jump_ms, elapsed_ms)
        #old_ms = self.jump_ms
        #self.jump_ms += elapsed_ms
        #if delta_h < MAX_FALLING_SPEED:
        #    delta_h = MAX_FALLING_SPEED
        #pos.y += delta_h
        #
        #if delta_h > 0:
        #    self.force.y = 1.0
        #elif delta_h < 0:
        #    self.force.y = -1.0
        #else:
        #    self.force.y = 0.0
        #
        #return old_ms < JUMP_DURATION <= self.jump_ms

        factor = self.get_gravity_growth_factor(elapsed_ms)

        if self.force.y == 0.0:
            # start falling
            self.force.y = -1.0  # FIXME: use constant
            return True

        old_force_y = self.force.y

        self.force.y -= 2.0 * elapsed_ms / 1000.0

        if self.force.y < -5:
            self.force.y = -5

        print(f'FORCE_Y: {self.force.y:.2f}')

        return old_force_y < 0 < self.force.y

    def apply_movement(self, pos: pygame.math.Vector2, elapsed_ms: int) -> None:
        if self.force.x > 0.0:
            self.face_x = FaceDirection.RIGHT
        elif self.force.x < 0.0:
            self.face_x = FaceDirection.LEFT

        pos.x += self.force.x * self.speed * MOVE_SPEED_FACTOR * elapsed_ms / 1000.0

        if self.force.y != 0.0:
            delta_y = self.get_jump_height_difference(elapsed_ms)
            print(f'DELTA: {delta_y:.2f}')
            #if delta_y < -3.5:
            #    delta_y = -3.5
            pos.y += delta_y
            print(f'POS_Y: {pos.y:.2f}')

        #pos += self.force * self.speed * MOVE_SPEED_FACTOR * elapsed_ms / 1000.0
