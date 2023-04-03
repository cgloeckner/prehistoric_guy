import pygame

from dataclasses import dataclass

from typing import Tuple, Optional


@dataclass
class Actor:
    # current position
    pos_x: float
    pos_y: float
    # movement vector
    force_x: float = 0.0
    force_y: float = 0.0
    jump_ms: int = 0


@dataclass
class Platform:
    left: float
    bottom: float
    width: float


def test_line_intersection(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float,
                           x4: float, y4: float) -> Optional[Tuple[float, float]]:
    """Tests whether the line from (x1, y1) to (x2, y2) intersects the line from (x3, y3) to (x4, y4).
    The corresponding linear equations system's solution is calculated.
    Returns (x, y) for the intersection position or None.
    """
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

    return x, y


# duration until the jump leads to falling
JUMP_DURATION: int = 500
GRAVITY: float = 9.81


def get_falling_distance(total_elapsed_ms: int) -> float:
    """Calculates falling distances using the 1st derivation of
    f(x) = -a * (t - 0.5s) ^2 + a
    where a full jump lasts 1s
    """
    return -GRAVITY * total_elapsed_ms / JUMP_DURATION + GRAVITY


class Platformer(object):
    """Manages physics simulation for the platforming scene.
    It holds actors and platforms, which have to be registered by appending them to the corresponding lists.
    """
    def __init__(self):
        self.actors = list()
        self.platforms = list()

    def update(self, elapsed_ms: int) -> None:
        """Update all actors' physics (jumping and falling) within the past view elapsed_ms.
        """
        for actor in self.actors:
            # trigger free fall if necessary
            if self.check_falling(actor):
                # as if at the highest point of a jump
                actor.force_y = -1.0
                actor.jump_ms = JUMP_DURATION

            # calculate movement vector
            move = pygame.math.Vector2(actor.force_x, actor.force_y * 3) * elapsed_ms * 0.005
            if move.y != 0.0:
                # continue jump and calculate y-speed
                actor.jump_ms += elapsed_ms
                move.y = get_falling_distance(actor.jump_ms) * 3 * 0.005

            # apply forces
            last_pos = pygame.math.Vector2(actor.pos_x, actor.pos_y)
            actor.pos_x += move.x
            actor.pos_y += move.y

            if move.y < 0:
                # while falling, check for collision against all platforms and pick the closest collision point
                stop_pos = self.check_collision(actor, last_pos)

                if stop_pos is not None:
                    actor.pos_x, actor.pos_y = stop_pos
                    actor.force_y = 0
                    actor.jump_ms = 0

    def check_falling(self, actor: Actor) -> bool:
        """The actor is falling if he does not stand on any platform.
        If the actor is jumping (force_y > 0) or already falling (force_y < 0), he is not falling.
        Returns True if he is falling.
        """
        if actor.force_y != 0:
            return False

        for platform in self.platforms:
            right = platform.left + platform.width
            if actor.pos_y - platform.bottom == 0.0 and platform.left <= actor.pos_x <= right:
                # actor stands on platform
                return False

        return True

    def check_collision(self, actor: Actor, last_pos: pygame.math.Vector2) -> Optional[pygame.math.Vector2]:
        """The actor's movement since his last_pos may collide with a platform.
        Returns the intersection point or None.
        """
        stop_pos = None
        stop_dist = None
        for platform in self.platforms:
            right = platform.left + platform.width
            pos = test_line_intersection(last_pos.x, last_pos.y, actor.pos_x, actor.pos_y,
                                         platform.left, platform.bottom, right, platform.bottom)
            if pos is not None:
                dist = pygame.math.Vector2(pos).distance_squared_to(last_pos)
                if stop_dist is None or dist < stop_dist:
                    stop_pos = pos
                    stop_dist = dist

        return stop_pos


if __name__ == '__main__':
    # minimal unit testing
    pos_x, pos_y = test_line_intersection(-3.5, 4, 4, -1, -3, -3, 4, 2)
    assert abs(pos_x - 1.8276) < 0.01
    assert abs(pos_y - 0.4483) < 0.01
