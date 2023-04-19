import pygame
from typing import Tuple

from platformer import physics, animations
from .context import Actor

DANGEROUS_HEIGHT: float = 1.5


def set_falling_from(actor: Actor, physics_actor: physics.Actor) -> None:
    actor.falling_from = physics_actor.pos.copy()


def get_falling_height(actor: Actor, pos: pygame.math.Vector2) -> float:
    """Calculates the vertical distance between falling_from and the given pos. If falling_from is None, the
    distance is 0.0.
    """
    if actor.falling_from is None:
        return 0.0
    delta_h = actor.falling_from.y - pos.y
    actor.falling_from = None
    return delta_h


def is_dangerous_height(height: float) -> bool:
    return height >= DANGEROUS_HEIGHT


def get_falling_damage(height: float) -> int:
    """Calculates falling damage based on falling height. Returns integer damage."""
    return int(height / 4.0)


def apply_landing(actor: Actor, physics_actor: physics.Actor) -> Tuple[animations.Action, int]:
    """Apply landing in terms of height and falling damage. A suitable animation action (IDLE or LANDING if it's
    been a dangerous height) and the damage taken are returned.
    """
    delta_h = get_falling_height(actor, physics_actor.pos)
    if not is_dangerous_height(delta_h):
        # safe height, IDLE is fine
        return (animations.Action.IDLE, 0)

    damage = get_falling_damage(delta_h)
    if damage > 0:
        actor.hit_points -= damage

    return (animations.Action.LANDING, damage)
