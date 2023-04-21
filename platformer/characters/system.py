from typing import Optional

from platformer import physics, animations
from . import Actor, EventListener, Context
from . import combat


class CharacterSystem:
    def __init__(self, listener: EventListener, context: Context, animations_context: animations.Context):
        self.listener = listener
        self.context = context
        self.animations_context = animations_context

    def apply_damage(self, victim: Actor, damage: int, cause: Optional[Actor] = None) -> None:
        if not combat.attack_enemy(damage, victim):
            return

        if victim.hit_points > 0:
            self.listener.on_char_damaged(victim, damage, cause)
        else:
            self.listener.on_char_died(victim, damage, cause)

    def apply_projectile_hit(self, victim: Actor, damage: int, proj: physics.Projectile) -> None:
        # try to find projectile's causing character
        cause = None
        if proj.from_actor is not None:
            cause = self.context.actors.get_by_id(proj.from_actor.object_id)

        self.apply_damage(victim, damage, cause)

    def update(self, elapsed_ms: int) -> None:
        pass
