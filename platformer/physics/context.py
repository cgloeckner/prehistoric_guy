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
    def on_grab(self, actor: actors.Actor) -> None:
        """Triggered when the actor grabs a ladder.
        """

    @abstractmethod
    def on_release(self, actor: actors.Actor) -> None:
        """Triggered when the actor released a ladder.
        """

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
    def on_impact_platform(self, projectile: projectiles.Projectile, platform: platforms.Platform) -> None:
        """Triggered when the projectile impact at the platform.
        """

    @abstractmethod
    def on_impact_actor(self, projectile: projectiles.Projectile, actor: actors.Actor) -> None:
        """Triggered when the projectile impact at the actor.
        """

    @abstractmethod
    def on_touch_object(self, actor: actors.Actor, obj: objects.Object) -> None:
        """Triggered when the actor touches at the object.
        """

    @abstractmethod
    def on_touch_actor(self, actor: actors.Actor, other: actors.Actor) -> None:
        """Triggered when the actor touches the other actor.
        """
