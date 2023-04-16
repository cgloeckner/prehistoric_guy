import pygame

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from platformer.physics import platforms
from platformer.physics import ladders
from platformer.physics import objects
from platformer.physics import actors
from platformer.physics import projectiles


@dataclass
class Context:
    def get_by_id(self, object_id: int) -> actors.Actor:
        for actor in self.actors:
            if actor.object_id == object_id:
                return actor

        # FIXME
        raise ValueError(f'No such Actor {object_id}')

    platforms: List[platforms.Platform]
    ladders: List[ladders.Ladder]
    objects: List[objects.Object]
    actors: List[actors.Actor]
    projectiles: List[projectiles.Projectile]


# ----------------------------------------------------------------------------------------------------------------------


class EventListener(ABC):

    @abstractmethod
    def on_falling(self, actor: actors.Actor) -> None:
        """Triggered when the actor starts falling.
        """

    @abstractmethod
    def on_landing(self, actor: actors.Actor) -> None:
        """Triggered when the actor lands on a platform.
        """

    @abstractmethod
    def on_collision(self, actor: actors.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor collides with the given platform.
        """

    @abstractmethod
    def on_grab(self, actor: actors.Actor) -> None:
        """Triggered when the actor grabs a ladder.
        """

    @abstractmethod
    def on_release(self, actor: actors.Actor) -> None:
        """Triggered when the actor released a ladder.
        """


# ----------------------------------------------------------------------------------------------------------------------


class System(object):
    def __init__(self, listener: EventListener, context: Context):
        self.listener = listener
        self.context = context

    def handle_actor_ladders(self, actor: actors.Actor) -> None:
        """Handles grabbing and releasing a ladder.
        """
        if actor.on_ladder is None:
            ladder = ladders.get_closest_ladder_in_reach(actor.pos, self.context.ladders)
            if ladder is not None:
                actor.on_ladder = ladder
                self.listener.on_grab(actor)

        # leaving ladder?
        if actor.on_ladder is not None:
            if not actor.on_ladder.is_in_reach_of(actor.pos):
                # reached end of ladder
                actor.on_ladder = None

    def handle_actor_gravity(self, actor: actors.Actor, elapsed_ms: int) -> None:
        """Handles gravity simulation.
        """
        if actor.can_fall():
            starts_falling = actor.movement.apply_gravity(elapsed_ms)
            if starts_falling:
                self.listener.on_falling(actor)

    @staticmethod
    def handle_actor_movement(actor: actors.Actor, elapsed_ms: int) -> pygame.math.Vector2:
        """Handles movement and jumping off a ladder.
        Returns the previous position.
        """
        # movement
        old_pos = actor.pos.copy()
        actor.movement.apply_movement(actor.pos, elapsed_ms, is_on_ladder=actor.on_ladder is not None)

        # moving off the ladder?
        if actor.on_ladder is not None:
            actor.movement.force.y = 0.0
            if actor.movement.force.x != 0.0:
                actor.on_ladder = None

        return old_pos

    def handle_actor_landing(self, actor: actors.Actor, old_pos: pygame.math.Vector2) -> None:
        """Handles landing on a platform.
        """
        # landing
        has_reloaded_support_platform = False
        platform = platforms.get_landing_platform(old_pos, actor.pos, self.context.platforms)
        if platform is not None:
            actor.land_on_platform(platform, old_pos)
            has_reloaded_support_platform = True
            self.listener.on_landing(actor)

        if not has_reloaded_support_platform:
            actor.on_platform = platforms.get_support_platform(actor.pos, self.context.platforms)

    def handle_actor_platform_collision(self, actor: actors.Actor, old_pos: pygame.math.Vector2) -> None:
        """Handles collision with platforms.
        """
        # platform collision
        platform = platforms.get_platform_collision(actor.pos, self.context.platforms)
        if platform is not None:
            actor.collide_with_platform(platform, old_pos)
            self.listener.on_collision(actor, platform)

    def update_actor(self, actor: actors.Actor, elapsed_ms: int) -> None:
        self.handle_actor_ladders(actor)
        self.handle_actor_gravity(actor, elapsed_ms)
        old_pos = self.handle_actor_movement(actor, elapsed_ms)

        if actor.on_ladder is None:
            self.handle_actor_landing(actor, old_pos)
            self.handle_actor_platform_collision(actor, old_pos)

    def update_projectile(self, proj: projectiles.Projectile, elapsed_ms: int) -> None:
        pass
        # FIXME: implement

    def update_hovering_platform(self, platform: platforms.Platform, elapsed_ms: int) -> None:
        if platform.hover is None:
            return

        # FIXME: implement

    def update(self, elapsed_ms: int) -> None:
        for actor in self.context.actors:
            self.update_actor(actor, elapsed_ms)

        for proj in self.context.projectiles:
            self.update_projectile(proj, elapsed_ms)

        for plat in self.context.platforms:
            self.update_hovering_platform(plat, elapsed_ms)
