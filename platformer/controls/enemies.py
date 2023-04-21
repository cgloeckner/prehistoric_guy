from dataclasses import dataclass

from core import objectids
from platformer import physics, animations, characters


@dataclass
class Enemy:
    object_id: int


# ----------------------------------------------------------------------------------------------------------------------


class EnemiesContext:
    def __init__(self):
        self.actors = objectids.IdList[Enemy]()

    def create_actor(self, object_id: int) -> Enemy:
        actor = Enemy(object_id=object_id)
        self.actors.append(actor)
        return actor


# ----------------------------------------------------------------------------------------------------------------------


class EnemiesSystem:
    def __init__(self, enemies_context: EnemiesContext, physics_context: physics.Context,
                 animations_context: animations.Context, characters_context: characters.Context):
        self.enemies_context = enemies_context
        self.physics_context = physics_context
        self.animations_context = animations_context
        self.characters_context = characters_context

    def update_actor(self, actor: Enemy, elapsed_ms: int) -> None:
        ani_enemy = self.animations_context.actors.get_by_id(actor.object_id)
        if ani_enemy.frame.action in [animations.Action.DIE, animations.Action.ATTACK, animations.Action.THROW,
                                      animations.Action.LANDING]:
            return

        phys_enemy = self.physics_context.actors.get_by_id(actor.object_id)
        if phys_enemy.on_platform is None:
            return

        char = self.characters_context.actors.get_by_id(actor.object_id)
        if char.hit_points == 0:
            return

        if phys_enemy.on_ladder is not None:
            # continue climbing down
            phys_enemy.move.force.y = -1.0
            ani_enemy.frame.start(animations.Action.CLIMB)
            return

        # move around
        left_bound = phys_enemy.on_platform.pos.x + phys_enemy.on_platform.width * 0.05
        right_bound = phys_enemy.on_platform.pos.x + phys_enemy.on_platform.width * 0.95
        if phys_enemy.pos.x < left_bound:
            phys_enemy.move.face_x = 1.0
        elif phys_enemy.pos.x > right_bound:
            phys_enemy.move.face_x = -1.0

        phys_enemy.move.force.x = phys_enemy.move.face_x
        ani_enemy.frame.start(animations.Action.MOVE)

    def update(self, elapsed_ms: int) -> None:
        for actor in self.enemies_context.actors:
            self.update_actor(actor, elapsed_ms)
