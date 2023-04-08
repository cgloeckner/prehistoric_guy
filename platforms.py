import pygame
import math
from dataclasses import dataclass
from typing import Tuple, Optional, List
from abc import abstractmethod


GRAVITY: float = 9.81

OBJECT_RADIUS: float = 0.25

# duration until the jump leads to falling
JUMP_DURATION: int = 500

# duration until another collision event is triggered
COLLISION_REPEAT_DELAY: int = 150

MOVE_SPEED_FACTOR: float = 3.5
JUMP_SPEED_FACTOR: float = 0.5


@dataclass
class Hovering:
    x: callable = None
    y: callable = None
    index: int = 0
    amplitude: float = 1.0


def get_hover_delta(hover: Hovering, elapsed_ms: int) -> Tuple[float, float]:
    # calculate movement delta
    angle = 2 * math.pi * hover.index / 360.0
    hover.index += 1
    x = 0
    y = 0
    if hover.x is not None:
        x = hover.x(angle) * elapsed_ms / 1000.0
    if hover.y is not None:
        y = hover.y(angle) * elapsed_ms / 1000.0
    x *= hover.amplitude
    y *= hover.amplitude

    return x, y


@dataclass
class Platform:
    # top left position
    x: float
    y: float
    # size
    width: int
    height: int = 0
    # floating information
    hover: Optional[Hovering] = None
    # editor UI related
    color: Optional[pygame.Color] = None


@dataclass
class Ladder:
    # bottom left position
    x: float
    y: float
    # size (uniform width)
    height: int


@dataclass
class Actor:
    id: int
    # bottom center position
    x: float
    y: float
    # movement vector
    face_x: float = 0.0
    force_x: float = 0.0
    force_y: float = 0.0
    jump_ms: int = 0
    fall_from_y: Optional[float] = None
    # collision data
    radius: float = 0.5
    anchor: Optional[Platform] = None
    ladder: Optional[Ladder] = None
    # prevents another collision/touch event for a couple of ms
    collision_repeat_cooldown: int = 0
    touch_repeat_cooldown: int = 0
    # editor UI related
    color: Optional[pygame.Color] = None


@dataclass
class Object:
    # position
    x: float
    y: float
    # object type id
    object_type: int
    # editor UI related
    color: Optional[pygame.Color] = None


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
    return platform.x <= actor.x < platform.x + platform.width and\
        platform.y - platform.height < actor.y < platform.y


def ladder_in_reach(actor: Actor, ladder: Ladder) -> bool:
    """Test whether the actor is in reach of the ladder.
    """
    return ladder.x <= actor.x < ladder.x + 1 and\
        ladder.y - actor.radius <= actor.y < ladder.y + ladder.height + OBJECT_RADIUS


def did_traverse_above(actor: Actor, last_pos: pygame.math.Vector2, platform: Platform) -> bool:
    """Test whether the actor moved through the top of the platform.
    """
    return actor.y <= platform.y < last_pos.y


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


def does_stand_on(actor: Actor, platform: Platform) -> bool:
    """Tests if the actor stands on the given platform or not.
    """
    if platform.y != actor.y:
        return False

    return platform.x <= actor.x <= platform.x + platform.width


class PhysicsListener(object):

    @abstractmethod
    def on_falling(self, actor: Actor) -> None:
        """Triggered when the actor starts falling.
        """
        pass

    @abstractmethod
    def on_land_on_platform(self, actor: Actor, platform: Platform) -> None:
        """Triggered when the actor landed on a platform.
        """
        pass

    @abstractmethod
    def on_collide_platform(self, actor: Actor, platform: Platform) -> None:
        """Triggered when the actor runs into a platform.
        """
        pass

    @abstractmethod
    def on_switch_platform(self, actor: Actor, platform: Platform) -> None:
        """Triggered when the actor switches to the given platform as an anchor.
        """
        pass

    @abstractmethod
    def on_touch_actor(self, actor: Actor, other: Actor) -> None:
        """Triggered when the actor touches another actor.
        """
        pass

    @abstractmethod
    def on_reach_object(self, actor: Actor, obj: Object) -> None:
        """Triggered when the actor reaches an object.
        """
        pass

    @abstractmethod
    def on_reach_ladder(self, actor: Actor, ladder: Ladder) -> None:
        """Triggered when the actor reaches a ladder.
        """
        pass

    @abstractmethod
    def on_leave_ladder(self, actor: Actor, ladder: Ladder) -> None:
        """Triggered when the actor leaves a ladder.
        """
        pass


class Physics(object):
    """Manages physics simulation for the platforming scene.
    It holds actors and platforms, which have to be registered by appending them to the corresponding lists.
    """
    def __init__(self, event_listener: PhysicsListener):
        self.actors = list()
        self.platforms = list()
        self.ladders = list()
        self.objects = list()

        self.event_listener = event_listener

    def get_supporting_platforms(self, actor: Actor) -> List[Platform]:
        """Returns a list of all platforms that will support the actor's position.
        """
        return [platform for platform in self.platforms if does_stand_on(actor, platform)]

    def anchor_actor(self, actor: Actor) -> None:
        """Tries to (re-)anchor the actor on a supporting platform.
        """
        relevant = self.get_supporting_platforms(actor)
        if len(relevant) == 0:
            actor.anchor = None
            return

        # pick any platform
        if actor.anchor == relevant[0]:
            return

        self.event_listener.on_switch_platform(actor, relevant[0])
        actor.anchor = relevant[0]

    def find_closest_ladder(self, actor: Actor) -> Optional[Ladder]:
        """Searches the closest ladder.
        Returns that ladder or None.
        """
        min_ladder = None
        min_dist = None
        for ladder in self.ladders:
            if not ladder_in_reach(actor, ladder):
                continue

            distance = abs(ladder.x - actor.x)
            if min_ladder is None or distance < min_dist:
                min_ladder = ladder
                min_dist = distance

        return min_ladder

    def grab_ladder(self, actor: Actor) -> None:
        """Tries to (re-)grab the closest ladder.
        Once a ladder is reached, on_reach_ladder is triggered.
        """
        closest_ladder = self.find_closest_ladder(actor)

        # notify reaching the new or leaving the old ladder
        if actor.ladder != closest_ladder:
            if closest_ladder is None:
                self.event_listener.on_leave_ladder(actor, closest_ladder)
                actor.force_y = 0
            else:
                self.event_listener.on_reach_ladder(actor, closest_ladder)

        actor.ladder = closest_ladder

    def is_falling(self, actor: Actor) -> bool:
        """The actor is falling if he does not stand on any platform.
        If the actor is jumping (force_y > 0) or already falling (force_y < 0), he is not falling.
        Returns True if he is falling.
        """
        if actor.ladder is not None:
            return False

        if actor.force_y != 0:
            return False

        return len(self.get_supporting_platforms(actor)) == 0

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

            pos = test_line_intersection(last_pos.x, last_pos.y, actor.x, actor.y, *top_left, *top_right)
            if pos is None:
                continue

            dist = pygame.math.Vector2(pos).distance_squared_to(last_pos)
            if stop_dist is None or dist < stop_dist:
                stop_pos = pos
                stop_dist = dist
                stop_platform = platform

        # reset position
        if stop_pos is not None:
            actor.x, actor.y = stop_pos

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
            actor.x, actor.y = last_pos

            return platform

    def simulate_gravity(self, actor: Actor, elapsed_ms: int) -> None:
        """This simulates the effect of gravity to an actor. This means adjusting the y-position by jumping and falling.
        Collision detection and handling is performed here. Further collision handling can be done using the
        on_land_on_platform callback of the event_listener.
        """
        if actor.ladder is not None:
            return

        if self.is_falling(actor):
            # as if at the highest point of a jump
            actor.force_y = -1.0
            actor.jump_ms = JUMP_DURATION
            actor.fall_from_y = actor.y
            self.event_listener.on_falling(actor)

        if actor.force_y == 0:
            return

        actor.anchor = None

        # calculate new height
        last_pos = pygame.math.Vector2(actor.x, actor.y)
        delta_height = get_falling_distance(actor.jump_ms, elapsed_ms) * JUMP_SPEED_FACTOR

        if delta_height < 0 and actor.fall_from_y is None:
            actor.fall_from_y = actor.y

        actor.jump_ms += elapsed_ms
        actor.y += delta_height

        # check for collision
        platform = self.check_falling_collision(actor, last_pos)
        if platform is None:
            # no collision detected
            return

        # reset position and jump
        actor.jump_ms = 0

        # trigger event
        actor.anchor = platform
        self.event_listener.on_land_on_platform(actor, platform)
        actor.fall_from_y = None

        # reset vertical force
        actor.force_y = 0

    def handle_movement(self, actor: Actor, elapsed_ms: int) -> None:
        """This handles the actor's horizontal movement. Collision is detected and handled. More collision handling
        can be achieved via on_collide_platform. Multiple calls are delayed with COLLISION_REPEAT_DELAY.
        """
        if actor.anchor is not None and actor.anchor.hover is not None:
            if actor.anchor.hover.x is not None:
                self.anchor_actor(actor)

        # look into current x-direction
        if actor.force_x != 0.0:
            actor.face_x = actor.force_x

        delta_x = actor.force_x * elapsed_ms * MOVE_SPEED_FACTOR / 1000
        if delta_x == 0.0:
            return

        # apply horizontal force
        last_pos = pygame.math.Vector2(actor.x, actor.y)
        actor.x += delta_x

        # check for collision against all platforms and pick the closest collision point
        platform = self.check_movement_collision(actor, last_pos)
        if platform is None:
            return

        # reset position
        actor.x, actor.y = last_pos
        self.anchor_actor(actor)

        # trigger event
        actor.touch_repeat_cooldown -= elapsed_ms
        if actor.touch_repeat_cooldown <= 0:
            actor.touch_repeat_cooldown = COLLISION_REPEAT_DELAY
            self.event_listener.on_collide_platform(actor, platform)

        # reset movement force
        actor.force_x = 0

    def handle_climb(self, actor: Actor, elapsed_ms: int) -> None:
        """Handles climbing on a ladder.
        If the ladder is left, on_leave_ladder is triggered.
        """
        self.grab_ladder(actor)

        if actor.force_x != 0.0:
            if actor.ladder is not None:
                self.event_listener.on_leave_ladder(actor, actor.ladder)
                actor.ladder = None
                actor.force_y = 0.0
            return

        if actor.ladder is None:
            return

        # reset falling
        actor.jump_ms = 0
        actor.fall_from_y = None

        delta_y = actor.force_y * elapsed_ms * MOVE_SPEED_FACTOR / 1000
        if delta_y == 0.0:
            return

        # stop climbing until triggered again
        actor.force_y = 0.0

        # apply horizontal force
        last_pos = pygame.math.Vector2(actor.x, actor.y)
        actor.y += delta_y

        if ladder_in_reach(actor, actor.ladder):
            return

        # search for platform to stand at
        relevant = self.get_supporting_platforms(actor)
        if len(relevant) > 0:
            actor.anchor = relevant[0]
            actor.ladder = None
            self.event_listener.on_leave_ladder(actor, actor.ladder)
            actor.force_y = 0.0
            return

        # reset actor to avoid leaving the ladder's end
        actor.force_y = 0.0
        actor.x, actor.y = last_pos
        print('reaching end of ladder', actor)


    def check_actor_collision(self, actor: Actor, elapsed_ms: int) -> None:
        """This checks for collisions between the actor and other actors in mutual distance. For each such collision,
        the callback on_touch_actor is triggered. Multiple calls are delayed with COLLISION_REPEAT_DELAY.
        """
        pos = pygame.math.Vector2(actor.x, actor.y)

        for other in self.actors:
            if actor == other:
                continue

            distance = pygame.math.Vector2(other.x, other.y).distance_squared_to(pos)
            if distance > (actor.radius + other.radius) ** 2:
                continue

            # trigger event
            actor.touch_repeat_cooldown -= elapsed_ms
            if actor.touch_repeat_cooldown <= 0:
                actor.touch_repeat_cooldown = COLLISION_REPEAT_DELAY
                self.event_listener.on_touch_actor(actor, other)

    def check_object_collision(self, actor: Actor) -> None:
        """This checks for collisions between the actor and other actors in mutual distance. For each such collision,
        the callback on_reach_object is triggered.
        """
        pos = pygame.math.Vector2(actor.x, actor.y + actor.radius)

        for other in self.objects:
            if actor == other:
                continue

            distance = pygame.math.Vector2(other.x, other.y).distance_squared_to(pos)
            if distance > (actor.radius * 2) ** 2:
                continue

            # trigger event
            self.event_listener.on_reach_object(actor, other)

    def simulate_floating(self, platform: Platform, elapsed_ms: int) -> None:
        if platform.hover is None or platform.hover.amplitude == 0.0:
            return

        delta_x, delta_y = get_hover_delta(platform.hover, elapsed_ms)

        # move platform
        platform.x += delta_x
        platform.y += delta_y

        # update actors who stand on it
        for actor in self.actors:
            if actor.anchor != platform:
                continue

            # apply
            last_pos = pygame.math.Vector2(actor.x, actor.y)
            actor.x += delta_x
            actor.y += delta_y

            # check for collision against all platforms and pick the closest collision point
            platform = self.check_movement_collision(actor, last_pos)
            if platform is None:
                continue

            # reset position
            actor.x, actor.y = last_pos

            # trigger event
            actor.touch_repeat_cooldown -= elapsed_ms
            if actor.touch_repeat_cooldown <= 0:
                actor.touch_repeat_cooldown = COLLISION_REPEAT_DELAY
                self.event_listener.on_collide_platform(actor, platform)

    def update(self, elapsed_ms: int) -> None:
        """Update all actors' physics (jumping and falling) within the past view elapsed_ms.
        """
        for actor in self.actors:
            self.simulate_gravity(actor, elapsed_ms)
            self.handle_movement(actor, elapsed_ms)
            self.handle_climb(actor, elapsed_ms)
            self.check_actor_collision(actor, elapsed_ms)
            self.check_object_collision(actor)

        for platform in self.platforms:
            self.simulate_floating(platform, elapsed_ms)

    def draw(self, target: pygame.Surface) -> None:
        """Performs debug drawing of shapes.
        """
        import pygame.gfxdraw
        from constants import WORLD_SCALE, OBJECT_SCALE

        for p in self.platforms:
            # draw platform's top, left and right edges
            x = p.x * WORLD_SCALE
            y = target.get_height() - p.y * WORLD_SCALE

            # draw hit box
            x2 = (p.x + p.width) * WORLD_SCALE
            y2 = target.get_height() - (p.y - p.height) * WORLD_SCALE
            pygame.draw.lines(target, 'red', False, ((x, y2), (x, y), (x2, y), (x2, y2)))

        for ladder in self.ladders:
            # top left position
            x = ladder.x * WORLD_SCALE
            y = target.get_height() - (ladder.y) * WORLD_SCALE

            w = WORLD_SCALE
            h = ladder.height * WORLD_SCALE
            pygame.gfxdraw.rectangle(target, (x, y, w, -h), pygame.Color('blue'))

        for obj in self.objects:
            # draw circular hit box (pos is bottom center, is moved to pure center)
            x = int(obj.x * WORLD_SCALE)
            y = int(target.get_height() - (obj.y * WORLD_SCALE + OBJECT_SCALE // 2))
            r = int(OBJECT_RADIUS * WORLD_SCALE)
            c = pygame.Color('gold')
            pygame.gfxdraw.circle(target, x, y, r, c)

        for actor in self.actors:
            # draw circular hit box (pos is bottom center, needs to be pure center)
            x = int(actor.x * WORLD_SCALE)
            y = int(target.get_height() - (actor.y * WORLD_SCALE + WORLD_SCALE // 2))
            r = int(actor.radius * WORLD_SCALE)
            c = pygame.Color('green')
            pygame.gfxdraw.circle(target, x, y, r, c)


if __name__ == '__main__':
    # minimal unit testing
    x, y = test_line_intersection(-3.5, 4, 4, -1, -3, -3, 4, 2)
    assert abs(x - 1.8276) < 0.01
    assert abs(y - 0.4483) < 0.01
