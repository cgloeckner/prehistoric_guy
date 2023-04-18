from typing import List, Generator

from core import objectids
from platformer import physics, animations
from .context import Actor, Context

# radius in which actors are within melee range
MELEE_ATTACK_RADIUS: float = 1.0

# force.y component for new projectiles, so they slightly rise during trajectory
PROJECTILE_DEFAULT_FORCE_Y: float = 0.5


def query_melee_range(actor: Actor, character_context: Context, physics_context: physics.Context) -> List[Actor]:
    """Returns all characters in melee range, using the physics system for query."""
    # query all physics actors in range
    phys_actor = physics_context.actors.get_by_id(actor.object_id)
    targets = phys_actor.get_all_faced_actors(physics_context.actors, MELEE_ATTACK_RADIUS)

    # query related characters
    in_range: List[Actor] = list()
    for other in targets:
        char = character_context.actors.get_by_id(other.object_id)
        if char is not None:
            in_range.append(char)

    return in_range


def attack_enemy(damage: int, victim: Actor) -> bool:
    """Returns True if the victim was hit."""
    if victim.hit_points == 0:
        # already incapacitated
        return False

    victim.hit_points -= damage
    return True


def throw_object(actor: Actor, projectile_speed: float, object_type: int, physics_context: physics.Context,
                 animations_context: animations.Context, id_generator: Generator[int, None, None]) -> physics.Projectile:
    """Creates a projectile originating at the given actor. Returns the created projectile, or None."""
    # prepare spawn pos at the center of the actor (rather midbottom)
    physics_actor = physics_context.actors.get_by_id(actor.object_id)
    pos = physics_actor.pos.copy()
    pos.y += physics_actor.radius

    # generate new projectile
    object_id = next(id_generator)
    physics_proj = physics_context.create_projectile(object_id=object_id, x=pos.x, y=pos.y, from_actor=physics_actor)
    animations_proj = animations_context.create_projectile(object_id=object_id)

    # more settings
    physics_proj.move.force.y = PROJECTILE_DEFAULT_FORCE_Y
    physics_proj.move.speed = projectile_speed
    physics_proj.object_type = object_type

    return physics_proj
