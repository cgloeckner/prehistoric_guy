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
    platforms: List[platforms.Platform]
    ladders: List[ladders.Ladder]
    objects: List[objects.Object]
    actors: List[actors.Actor]
    projectiles: List[projectiles.Projectile]

    def get_by_id(self, object_id: int) -> actors.Actor:
        for actor in self.actors:
            if actor.object_id == object_id:
                return actor

        # FIXME
        raise ValueError(f'No such Actor {object_id}')


# ----------------------------------------------------------------------------------------------------------------------


class EventListener(ABC):

    @abstractmethod
    def on_falling(self, actor: actors.Actor) -> None:
        """Triggered when the actor starts falling.
        """

    @abstractmethod
    def on_collision(self, actor: actors.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor collides with the given platform.
        """

    @abstractmethod
    def on_landing(self, actor: actors.Actor) -> None:
        """Triggered when the actor lands on a platform.
        """


# ----------------------------------------------------------------------------------------------------------------------


class System(object):
    def __init__(self, listener: EventListener, context: Context):
        self.listener = listener
        self.context = context

    def update_actor(self, actor: actors.Actor, elapsed_ms: int) -> None:
        # handle gravity and movement
        if actor.can_fall():
            if actor.movement.apply_gravity(actor.pos, elapsed_ms):
                # notify falling
                self.listener.on_falling(actor)

        old_pos = actor.pos.copy()
        actor.movement.apply_movement(actor.pos, elapsed_ms)

        reloaded_support = False

        if actor.movement.force.y < 0.0:
            # check for landing
            platform = platforms.get_closest_platform_traversed_from_above(old_pos, actor.pos, self.context.platforms)
            #print(old_pos, actor.pos)
            #print(f'land {platform}')
            if platform is not None:
                # calculate landing position
                landing_pos = platform.get_landing_point(old_pos, actor.pos)
                if landing_pos is not None:
                    # land on platform
                    actor.pos = landing_pos.copy()
                    actor.movement.force = pygame.math.Vector2()
                    actor.on_platform = platform
                    actor.jump_ms = 0
                    #print('landed')
                    reloaded_support = True
                    self.listener.on_landing(actor)

        if actor.movement.force.x != 0.0:
            if not reloaded_support:
                # refresh support platform
                actor.on_platform = platforms.get_any_platform_supporting_point(actor.pos, self.context.platforms)

            # check for collisions
            platform = platforms.get_any_colliding_platform(actor.pos, self.context.platforms)
            if platform is not None:
                # collide with platform
                actor.pos = old_pos.copy()
                actor.movement.force.x = 0.0
                actor.on_platform = platform
                self.listener.on_collision(actor, platform)

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
