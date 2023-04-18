import pygame
from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod

from core import objectids, bounded_value


@dataclass
class Actor:
    object_id: int

    hit_points: bounded_value.Int = field(default_factory=lambda: bounded_value.Int(1, 1))
    num_axes: bounded_value.Int = field(default_factory=lambda: bounded_value.Int(0, 0))

    falling_from: Optional[pygame.math.Vector2] = None  # position from which the actor started falling earlier


class Context:
    def __init__(self):
        self.actors = objectids.IdList[Actor]()

    def create_actor(self, object_id: int, max_hit_points: int, num_axes: int) -> Actor:
        actor = Actor(object_id=object_id, hit_points=bounded_value.Int(max_hit_points, max_hit_points),
                      num_axes=bounded_value.Int(num_axes, num_axes))
        self.actors.append(actor)
        return actor


class EventListener(ABC):

    @abstractmethod
    def on_char_damaged(self, actor: Actor, damage: int, cause: Optional[Actor]) -> None:
        """Triggered when an actor got damaged."""
        pass

    @abstractmethod
    def on_char_died(self, actor: Actor, damage: int, cause: Optional[Actor]) -> None:
        """Triggered when an actor died. An optional cause can be provided."""
        pass
