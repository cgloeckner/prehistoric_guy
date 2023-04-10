from dataclasses import dataclass
from typing import Optional
from abc import abstractmethod

from platformer import physics


NO_ACTION: int = 0
ATTACK_ACTION: int = 1
THROW_ACTION: int = 2

DANGEROUS_HEIGHT: float = 1.5


@dataclass
class Actor:
    object_id: int

    hit_points: int = 5
    max_hit_points: int = hit_points
    num_axes: int = 5
    max_num_axes: int = num_axes


def get_falling_damage(height: float) -> int:
    """Calculates falling damage based on falling height.
    Returns integer damage.
    """
    return int(height / 4.0)


def apply_damage(actor: Actor, damage: int) -> None:
    actor.hit_points -= abs(damage)
    if actor.hit_points < 0:
        actor.hit_points = 0


class CharacterListener(object):

    @abstractmethod
    def on_char_damaged(self, actor: Actor, damage: int) -> None:
        """Triggered when an actor got damaged.
        """
        pass

    @abstractmethod
    def on_char_died(self, actor: Actor, cause: Optional[Actor]) -> None:
        """Triggered when an actor died. An optional cause can be provided.
        """
        pass


class Characters(object):
    def __init__(self, event_listener: CharacterListener):
        self.event_listener = event_listener
        self.characters = list()

    def get_by_id(self, object_id: int) -> Actor:
        """Returns the actor who matches the given object_id.
        May throw an IndexError.
        """
        return [a for a in self.characters if a.object_id == object_id][0]

    def try_get_by_id(self, object_id: int) -> Optional[Actor]:
        """Returns the actor who matches the given object_id or None
        """
        try:
            return self.get_by_id(object_id)
        except IndexError:
            return None

    def apply_projectile_hit(self, victim: Actor, proj: physics.Projectile) -> None:
        pass

    def apply_falling_damage(self, victim: Actor, damage: int, cause: Optional[Actor] = None) -> None:
        apply_damage(victim, damage)
        if victim.hit_points > 0:
            self.event_listener.on_char_damaged(victim, damage)
        else:
            self.event_listener.on_char_died(victim, cause)

    def update(self, elapsed_ms: int) -> None:
        # FIXME: damage over time (e.g. poison)?
        pass
