import pygame
from dataclasses import dataclass
from typing import Tuple, Optional


GRAVITY: float = 9.81

# duration until the jump leads to falling
JUMP_DURATION: int = 500

# duration until another collision event is triggered
COLLISION_REPEAT_DELAY: int = 150


@dataclass
class Actor:
    # current position
    pos_x: float
    pos_y: float
    # movement vector
    force_x: float = 0.0
    force_y: float = 0.0
    jump_ms: int = 0
    # collision data
    radius: float = 0.25
    # prevents another collision/touch event for a couple of ms
    collision_repeat_cooldown: int = 0
    touch_repeat_cooldown: int = 0


@dataclass
class Object:
    # position
    pos_x: float
    pos_y: float
    # object type id
    object_type: int


@dataclass
class Platform:
    # top left position
    x: float
    y: float
    # size
    width: int
    height: int


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


def is_inside_platform(actor: Actor, platform: Platform) -> bool:
    """Test whether the actor is inside the platform.
    """
    return platform.x <= actor.pos_x < platform.x + platform.width and\
        platform.y - platform.height < actor.pos_y < platform.y


def did_traverse_above(actor: Actor, last_pos: pygame.math.Vector2, platform: Platform) -> bool:
    """Test whether the actor moved through the top of the platform.
    """
    return actor.pos_y <= platform.y < last_pos.y


def get_falling_distance(elapsed_ms: int, delta_ms: int) -> float:
    """Calculates falling distances using
    f(x) = -a * (t - 0.5s) ^ 2 + a * 0.25
    where a full jump lasts 1s
    """
    def f(x):
        return -GRAVITY * (x / JUMP_DURATION - 0.5) ** 2 + GRAVITY * 0.25

    # cap maximum falling speed
    if elapsed_ms > 2000:
        elapsed_ms = 2000

    old_h = f(elapsed_ms)
    new_h = f(elapsed_ms + delta_ms)
    return new_h - old_h


class Physics(object):
    """Manages physics simulation for the platforming scene.
    It holds actors and platforms, which have to be registered by appending them to the corresponding lists.
    """
    def __init__(self, on_landed: callable, on_collision: callable, on_touch: callable, on_reach: callable):
        self.actors = list()
        self.platforms = list()
        self.objects = list()

        self.on_landed = on_landed
        self.on_collision = on_collision
        self.on_touch = on_touch
        self.on_reach = on_reach

    def is_falling(self, actor: Actor) -> bool:
        """The actor is falling if he does not stand on any platform.
        If the actor is jumping (force_y > 0) or already falling (force_y < 0), he is not falling.
        Returns True if he is falling.
        """
        if actor.force_y != 0:
            return False

        for platform in self.platforms:
            right = platform.x + platform.width
            if actor.pos_y - platform.y == 0.0 and platform.x <= actor.pos_x <= right:
                # actor stands on platform
                return False

        return True

    def check_falling_collision(self, actor: Actor, last_pos: pygame.math.Vector2) -> Optional[Platform]:
        """The actor has fallen from his last_pos and may have collided with the top of a platform. If such a platform
        is found, the actor is automatically adjusted to his landing point on top of that platform.
        Returns a platform or None.
        """
        stop_pos = None
        stop_dist = None
        stop_platform = None

        # check for platform traversal via line intersections
        for platform in (p for p in self.platforms if did_traverse_above(actor, last_pos, p)):
            # create relevant lines from platform's vertices
            top_left = (platform.x, platform.y)
            top_right = (platform.x + platform.width, platform.y)

            pos = test_line_intersection(last_pos.x, last_pos.y, actor.pos_x, actor.pos_y, *top_left, *top_right)
            if pos is None:
                continue

            dist = pygame.math.Vector2(pos).distance_squared_to(last_pos)
            if stop_dist is None or dist < stop_dist:
                stop_pos = pos
                stop_dist = dist
                stop_platform = platform

        # reset position
        if stop_pos is not None:
            actor.pos_x, actor.pos_y = stop_pos

        return stop_platform

    def check_movement_collision(self, actor: Actor, last_pos: pygame.math.Vector2) -> Platform:
        """The actor has moved from last_pos horizontally. Meanwhile, he may have collided with a platform. If such a
        platform is found, the actor's position is automatically reset to the last_pos.
        Returns a platform or None.
        """
        for platform in self.platforms:
            if not is_inside_platform(actor, platform):
                continue

            # reset position
            actor.pos_x, actor.pos_y = last_pos

            return platform

    def simulate_gravity(self, actor: Actor, elapsed_ms: int) -> None:
        """This simulates the effect of gravity to an actor. This means adjusting the y-position by jumping and falling.
        Collision detection and handling is performed here. Further collision handling can be done using the on_landed
        callback.
        """
        if self.is_falling(actor):
            # as if at the highest point of a jump
            actor.force_y = -1.0
            actor.jump_ms = JUMP_DURATION

        if actor.force_y == 0:
            return

        # calculate new height
        last_pos = pygame.math.Vector2(actor.pos_x, actor.pos_y)
        delta_height = get_falling_distance(actor.jump_ms, elapsed_ms)
        actor.jump_ms += elapsed_ms
        actor.pos_y += delta_height

        # check for collision
        platform = self.check_falling_collision(actor, last_pos)
        if platform is None:
            # no collision detected
            return

        # reset position and jump
        actor.jump_ms = 0

        # trigger event
        self.on_landed(actor, platform)

        # reset vertical force
        actor.force_y = 0

    def handle_movement(self, actor: Actor, elapsed_ms: int) -> None:
        """This handles the actor's horizontal movement. Collision is detected and handled. More collision handling
        can be achieved via on_collision. Multiple calls are delayed with COLLISION_REPEAT_DELAY
        """
        delta_x = actor.force_x * elapsed_ms * 0.0075
        if delta_x == 0.0:
            return

        # apply horizontal force
        last_pos = pygame.math.Vector2(actor.pos_x, actor.pos_y)
        actor.pos_x += delta_x

        # check for collision against all platforms and pick the closest collision point
        platform = self.check_movement_collision(actor, last_pos)
        if platform is None:
            return

        # reset position
        actor.pos_x, actor.pos_y = last_pos

        # trigger event
        actor.touch_repeat_cooldown -= elapsed_ms
        if actor.touch_repeat_cooldown <= 0:
            actor.touch_repeat_cooldown = COLLISION_REPEAT_DELAY
            self.on_collision(actor, platform)

        # reset movement force
        actor.force_x = 0

    def check_actor_collision(self, actor: Actor, elapsed_ms: int) -> None:
        """This checks for collisions between the actor and other actors in mutual distance. For each such collision,
        the callback on_touch is triggered. Multiple calls are delayed with COLLISION_REPEAT_DELAY.
        """
        pos = pygame.math.Vector2(actor.pos_x, actor.pos_y)

        for other in self.actors:
            if actor == other:
                continue

            distance = pygame.math.Vector2(other.pos_x, other.pos_y).distance_squared_to(pos)
            if distance > (actor.radius + other.radius) ** 2:
                continue

            # trigger event
            actor.touch_repeat_cooldown -= elapsed_ms
            if actor.touch_repeat_cooldown <= 0:
                actor.touch_repeat_cooldown = COLLISION_REPEAT_DELAY
                self.on_touch(actor, other)

    def check_object_collision(self, actor: Actor) -> None:
        """This checks for collisions between the actor and other actors in mutual distance. For each such collision,
        the callback on_reach is triggered.
        """
        pos = pygame.math.Vector2(actor.pos_x, actor.pos_y + actor.radius)

        for other in self.objects:
            if actor == other:
                continue

            distance = pygame.math.Vector2(other.pos_x, other.pos_y).distance_squared_to(pos)
            if distance > (actor.radius * 2) ** 2:
                continue

            # trigger event
            self.on_reach(actor, other)

    def update(self, elapsed_ms: int) -> None:
        """Update all actors' physics (jumping and falling) within the past view elapsed_ms.
        """
        for actor in self.actors:
            self.simulate_gravity(actor, elapsed_ms)
            self.handle_movement(actor, elapsed_ms)
            self.check_actor_collision(actor, elapsed_ms)
            self.check_object_collision(actor)


if __name__ == '__main__':
    # minimal unit testing
    pos_x, pos_y = test_line_intersection(-3.5, 4, 4, -1, -3, -3, 4, 2)
    assert abs(pos_x - 1.8276) < 0.01
    assert abs(pos_y - 0.4483) < 0.01
