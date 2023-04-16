import pygame
import math
from dataclasses import dataclass
from typing import Tuple, Optional, List
from abc import ABC, abstractmethod

from core import resources
from core import shapes



def get_jump_height_difference(elapsed_ms: int, delta_ms: int) -> float:
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



class EventListener(ABC):

    # --- gravity-related ----------------------------------------------------------------------------------------------

    @abstractmethod
    def on_jumping(self, actor: Actor) -> None:
        """Triggered when the actor starts jumping.
        """
        pass

    @abstractmethod
    def on_falling(self, actor: Actor) -> None:
        """Triggered when the actor starts falling.
        """
        pass

    @abstractmethod
    def on_landing(self, actor: Actor) -> None:
        """Triggered when the actor landed on a platform.
        """
        pass

    # --- others -------------------------------------------------------------------------------------------------------

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

    @abstractmethod
    def on_impact_platform(self, proj: Projectile, platform: Platform) -> None:
        """Triggered when a projectile hits a platform.
        """
        pass

    @abstractmethod
    def on_impact_actor(self, proj: Projectile, actor: Actor) -> None:
        """Triggered when a projectile hits an actor.
        """
        pass


class Physics(object):
    """Manages physics simulation for the platforming scene.
    It holds actors and platforms, which have to be registered by appending them to the corresponding lists.
    """
    def __init__(self, event_listener: EventListener):
        self.actors: List[Actor] = list()
        self.platforms: List[Platform] = list()
        self.ladders: List[Ladder] = list()
        self.objects: List[Object] = list()
        self.projectiles: List[Projectile] = list()

        self.event_listener = event_listener

    def get_by_id(self, object_id: int) -> Actor:
        """Returns the actor who matches the given object_id.
        May throw an IndexError.
        """
        return [a for a in self.actors if a.object_id == object_id][0]

    # --- gravity-related ----------------------------------------------------------------------------------------------

    def start_jumping(self, actor: Actor) -> None:
        actor.ladder = None
        actor.anchor = None
        actor.fall_from_y = None
        actor.jump_ms = 0
        self.event_listener.on_jumping(actor)

    def start_falling(self, actor: Actor) -> None:
        actor.force_y = -1.0
        actor.jump_ms = JUMP_DURATION  # as if at the highest point of a jump
        actor.fall_from_y = actor.y
        self.event_listener.on_falling(actor)

    def stop_falling(self, actor: Actor) -> None:
        actor.force_y = 0.0
        actor.jump_ms = 0
        if actor.fall_from_y != actor.y:
            self.event_listener.on_landing(actor)
        actor.fall_from_y = None

    def check_falling_collision(self, actor: Actor, last_pos: pygame.math.Vector2) -> Optional[Platform]:
        """Searches for the closest platform that is traversed while falling. If such a platform is found, the actor
        is automatically reset to the last_pos.
        Returns a platform or None.
        """
        stop_pos = None
        stop_dist = None
        stop_platform = None

        # check for platform traversal via line intersections
        for platform in self.platforms:
            if not did_traverse_above(actor.x, actor.y, last_pos, platform):
                continue

            # create relevant line from platform's vertices
            y_top = platform.y + platform.height
            top_line = shapes.Line(platform.x, y_top, platform.x + platform.width, y_top)
            move_line = shapes.Line(actor.x, actor.y, *last_pos)

            pos = top_line.collideline(move_line)
            if pos is None:
                continue

            dist = pygame.math.Vector2(pos).distance_squared_to(last_pos)
            if stop_dist is None or dist < stop_dist:
                # found closer platform
                stop_pos = pos
                stop_dist = dist
                stop_platform = platform

        # reset position
        if stop_pos is not None:
            actor.x, actor.y = stop_pos

        return stop_platform

    def simulate_gravity(self, actor: Actor, elapsed_ms: int) -> None:
        """This simulates the effect of gravity to an actor. This means adjusting the y-position by jumping and falling.
        Collision detection and handling is performed here. Further collision handling can be done using the
        on_land_on_platform callback of the event_listener.
        """
        if actor.ladder is not None:
            # actor is supported by a ladder, so no gravity is applied
            return

        if actor.force_y > 0.0 and actor.jump_ms == 0:
            self.start_jumping(actor)

        if actor.anchor is not None:
            # actor is supported by a platform, so no gravity is applied
            return

        if actor.force_y == 0.0:
            self.start_falling(actor)

        # apply gravity
        last_pos = pygame.math.Vector2(actor.x, actor.y)
        delta_height = get_jump_height_difference(actor.jump_ms, elapsed_ms) * JUMP_SPEED_FACTOR

        if actor.fall_from_y is None and delta_height < 0:
            self.start_falling(actor)

        actor.jump_ms += elapsed_ms
        actor.y += delta_height

        # check for landing on a platform
        platform = self.check_falling_collision(actor, last_pos)
        if platform is None:
            return

        # reset jump duration and vertical force when landing
        actor.anchor = platform
        self.stop_falling(actor)

    # --- movement-related ---------------------------------------------------------------------------------------------

    def get_supporting_platforms(self, actor: Actor) -> Optional[Platform]:
        """Returns the next best supporting platform or None.
        """
        for platform in self.platforms:
            if does_stand_on(actor, platform):
                return platform

        return None

    def anchor_actor(self, actor: Actor) -> None:
        """Tries to (re-)anchor the actor on a supporting platform.
        """
        platform = self.get_supporting_platforms(actor)
        if platform is None:
            # release from previous anchor
            actor.anchor = None
            return

        if actor.anchor == platform:
            # keep previous anchor
            return

        # switch platforms
        self.event_listener.on_switch_platform(actor, platform)
        actor.anchor = platform

    def check_movement_collision(self, actor: Actor) -> Optional[Platform]:
        """The actor has moved from last_pos horizontally. Meanwhile, he may have collided with a tile.
        Returns a platform or None.
        """
        for platform in self.platforms:
            if is_inside_platform(actor.x, actor.y, platform):
                return platform

    def handle_movement(self, actor: Actor, elapsed_ms: int) -> None:
        """This handles the actor's horizontal movement. Collision is detected and handled. More collision handling
        can be achieved via on_collide_platform. Multiple calls are delayed with COLLISION_REPEAT_DELAY.
        """
        # look into current x-direction
        if actor.force_x != 0.0:
            actor.face_x = actor.force_x

        # apply movement and pick anchoring platform
        delta_x = actor.force_x * elapsed_ms * MOVE_SPEED_FACTOR / 1000
        if delta_x == 0.0:
            return

        last_pos = pygame.math.Vector2(actor.x, actor.y)
        actor.x += delta_x
        self.anchor_actor(actor)

        # check for collision with platform
        platform = self.check_movement_collision(actor)
        if platform is None:
            return

        # reset position and stop movement on collision
        actor.x, actor.y = last_pos
        actor.force_x = 0.0
        actor.touch_repeat_cooldown -= elapsed_ms
        if actor.touch_repeat_cooldown <= 0:
            actor.touch_repeat_cooldown = COLLISION_REPEAT_DELAY
            self.event_listener.on_collide_platform(actor, platform)

    # --- ladder-related -----------------------------------------------------------------------------------------------

    def find_ladder(self, actor: Actor) -> Optional[Ladder]:
        """Searches the closest ladder.
        Returns that ladder or None.
        """
        min_ladder = None
        min_dist = None
        for ladder in self.ladders:
            if not ladder_in_reach(actor.x, actor.y, ladder):
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
        closest_ladder = self.find_ladder(actor)

        # notify reaching the new or leaving the old ladder
        old_ladder = actor.ladder
        actor.ladder = closest_ladder

        if old_ladder != closest_ladder:
            if closest_ladder is None:
                self.event_listener.on_leave_ladder(actor, old_ladder)
                actor.force_y = 0
            else:
                self.event_listener.on_reach_ladder(actor, closest_ladder)

    def handle_ladder(self, actor: Actor, elapsed_ms: int) -> None:
        """Handles climbing on a ladder. Leaving a ladder triggers on_leave_ladder.
        """
        self.grab_ladder(actor)

        if actor.ladder is None:
            return

        # reset falling
        actor.jump_ms = 0
        actor.fall_from_y = None

        # handle climbing
        delta_y = actor.force_y * elapsed_ms * CLIMB_SPEED_FACTOR / 1000
        if delta_y == 0.0:
            return

        # stop climbing until triggered again
        actor.force_y = 0.0

        # apply horizontal force
        actor.y += delta_y
        self.anchor_actor(actor)

        if ladder_in_reach(actor.x, actor.y, actor.ladder):
            return

        if actor.y >= actor.ladder.y + actor.ladder.height:
            # upper end is safe
            actor.y = actor.ladder.y + actor.ladder.height
            self.anchor_actor(actor)
            return

        # lower end: avoid jumping off
        actor.y = actor.ladder.y
        self.anchor_actor(actor)

    # --- collision-related --------------------------------------------------------------------------------------------

    def check_actor_collision(self, actor: Actor, elapsed_ms: int) -> None:
        """This checks for collisions between the actor and other actors in mutual distance. For each such collision,
        the callback on_touch_actor is triggered. Multiple calls are delayed with COLLISION_REPEAT_DELAY.
        """
        circ1 = get_actor_circ(actor)

        for other in self.actors:
            if actor == other:
                continue

            circ2 = get_actor_circ(other)
            if not circ1.collidecirc(circ2):
                continue

            # trigger event
            actor.touch_repeat_cooldown -= elapsed_ms
            if actor.touch_repeat_cooldown <= 0:
                actor.touch_repeat_cooldown = COLLISION_REPEAT_DELAY
                self.event_listener.on_touch_actor(actor, other)

    def check_object_collision(self, actor: Actor, elapsed_ms) -> None:
        """This checks for collisions between the actor and other actors in mutual distance. For each such collision,
        the callback on_reach_object is triggered.
        """
        circ1 = get_actor_circ(actor)

        for other in self.objects:
            if actor == other:
                continue

            circ2 = get_object_circ(other)
            if not circ1.collidecirc(circ2):
                continue

            # trigger event

            actor.touch_repeat_cooldown -= elapsed_ms
            if actor.touch_repeat_cooldown <= 0:
                actor.touch_repeat_cooldown = COLLISION_REPEAT_DELAY
                self.event_listener.on_reach_object(actor, other)

    def update_projectile(self, proj: Projectile, elapsed_ms: int) -> None:
        """Update a projectile's ballistic trajectory.
        """
        if proj.face_x == 0.0:
            return

        last_pos = pygame.math.Vector2(proj.x, proj.y)

        proj.x += proj.face_x * PROJECTILE_SPEED * elapsed_ms / 1000.0
        proj.y += get_jump_height_difference(proj.fly_ms, elapsed_ms) * PROJECTILE_GRAVITY
        proj.fly_ms += elapsed_ms

        circ1 = get_projectile_circ(proj)
        for actor in self.actors:
            if actor == proj.from_actor or not actor.can_collide:
                # ignore projectile's origin
                continue

            circ2 = get_actor_circ(actor)
            if circ1.collidecirc(circ2):
                # collision with actor
                self.event_listener.on_impact_actor(proj, actor)

        for platform in self.platforms:
            # FIXME: replace face_x with force_x, force_y to allow diagonal proj., so did_traverse_above makes sense
            if is_inside_platform(proj.x, proj.y, platform) or did_traverse_above(proj.x, proj.y, last_pos, platform):
                # collision with platform
                self.event_listener.on_impact_platform(proj, platform)
                proj.x, proj.y = last_pos.xy
                proj.face_x = 0.0


    # --- floating platforms -------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------

    def update(self, elapsed_ms: int) -> None:
        """Update all actors' physics (jumping and falling) within the past view elapsed_ms.
        """
        for actor in self.actors:
            self.simulate_gravity(actor, elapsed_ms)
            self.handle_movement(actor, elapsed_ms)
            self.handle_ladder(actor, elapsed_ms)
            self.check_actor_collision(actor, elapsed_ms)
            self.check_object_collision(actor, elapsed_ms)

        for proj in self.projectiles:
            self.update_projectile(proj, elapsed_ms)

        for platform in self.platforms:
            self.simulate_floating(platform, elapsed_ms)
