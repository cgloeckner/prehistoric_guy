import pygame

from abc import ABC, abstractmethod
from typing import List, Optional

from platformer.physics import platforms
from platformer.physics import ladders
from platformer.physics import objects
from platformer.physics import actors
from platformer.physics import projectiles


class Context:
    def __init__(self):
        self.platforms: List[platforms.Platform] = list()
        self.ladders: List[ladders.Ladder] = list()
        self.objects: List[objects.Object] = list()
        self.actors: List[actors.Actor] = list()
        self.projectiles: List[projectiles.Projectile] = list()

    def get_actor_by_id(self, object_id: int) -> actors.Actor:
        for actor in self.actors:
            if actor.object_id == object_id:
                return actor

        # FIXME
        raise ValueError(f'No such Actor {object_id}')

    def get_projectile_by_id(self, object_id: int) -> projectiles.Projectile:
        for proj in self.projectiles:
            if proj.object_id == object_id:
                return proj

        # FIXME
        raise ValueError(f'No such Actor {object_id}')

    def create_platform(self, x: float, y: float, width: int, height: int = 0,
                        hover: Optional[platforms.Hovering] = None) -> platforms.Platform:
        p = platforms.Platform(pos=pygame.math.Vector2(x, y), width=width, height=height, hover=hover)
        self.platforms.append(p)
        return p

    def create_ladder(self, x: float, y: float, height: int) -> ladders.Ladder:
        ladder = ladders.Ladder(pos=pygame.math.Vector2(x, y), height=height)
        self.ladders.append(ladder)
        return ladder

    def create_object(self, x: float, y: float, object_type: objects.ObjectType) -> objects.Object:
        o = objects.Object(pos=pygame.math.Vector2(x, y), object_type=object_type)
        self.objects.append(o)
        return o

    def create_actor(self, object_id: int, x: float, y: float) -> actors.Actor:
        a = actors.Actor(object_id=object_id, pos=pygame.math.Vector2(x, y))
        self.actors.append(a)
        return a

    def create_projectile(self, object_id: int, x: float, y: float, from_actor: Optional[actors.Actor] = None) \
            -> projectiles.Projectile:
        p = projectiles.Projectile(object_id=object_id, pos=pygame.math.Vector2(x, y), from_actor=from_actor)
        self.projectiles.append(p)
        if from_actor is not None:
            p.movement.face_x = from_actor.movement.face_x
            p.movement.force.x = p.movement.face_x
        return p

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
