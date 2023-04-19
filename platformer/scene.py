import pygame
from typing import Optional

from core import constants, resources

from . import physics, animations, characters

from .factory import EventListener, Factory


class Scene(EventListener):
    def __init__(self, cache: resources.Cache, target: pygame.Surface):
        self.factory = Factory(self, cache, target)

    def on_grab(self, actor: physics.Actor) -> None:
        """Triggered when the actor grabs a ladder."""
        player = self.factory.ctx.players.actors.get_by_id(actor.object_id)
        if player is not None:
            return

        # enemy! let 'm climb
        actor.pos.x = actor.on_ladder.pos.x
        actor.move.force.x = 0.0
        actor.move.force.y = 0.0
        ani_enemy = self.factory.ctx.animations.actors.get_by_id(actor.object_id)
        ani_enemy.frame.start(animations.Action.IDLE)

    def on_release(self, actor: physics.Actor) -> None:
        """Triggered when the actor releases a ladder."""
        pass

    def on_falling(self, phys_actor: physics.Actor) -> None:
        """Triggered when the actor starts falling."""
        actor = self.factory.ctx.characters.actors.get_by_id(phys_actor.object_id)
        characters.set_falling_from(actor, phys_actor)

    def on_landing(self, phys_actor: physics.Actor) -> None:
        """Triggered when the actor landed on a platform."""
        actor = self.factory.ctx.characters.actors.get_by_id(phys_actor.object_id)
        action, damage = characters.apply_landing(actor, phys_actor)
        ani_actor = self.factory.ctx.animations.actors.get_by_id(phys_actor.object_id)

        if damage > 0:
            if actor.hit_points == 0:
                self.on_char_died(actor, damage, None)
            else:
                self.on_char_damaged(actor, damage, None)

        else:
            ani_actor.frame.start(action)

    def on_collision(self, actor: physics.Actor, platform: physics.Platform) -> None:
        """Triggered when the actor runs into a platform."""
        pass

    def on_touch_object(self, phys_actor: physics.Actor, obj: physics.Object) -> None:
        """Triggered when the actor reaches an object."""
        char_actor = self.factory.ctx.characters.actors.get_by_id(phys_actor.object_id)
        if char_actor is not None:
            if obj.object_type == constants.ObjectType.FOOD:
                # heal him
                char_actor.hit_points += 1
                # FIXME: on_player_healed

            elif obj.object_type == constants.ObjectType.WEAPON:
                # grab axe
                char_actor.num_axes += 1
                # FIXME: on_weapon_collected

        self.factory.ctx.physics.objects.remove(obj)
        self.factory.create_random_object()

    def on_impact_platform(self, proj: physics.Projectile, platform: physics.Platform) -> None:
        """Triggered when a projectile hits a platform."""
        self.factory.ctx.physics.create_object(x=proj.pos.x, y=proj.pos.y - constants.OBJECT_RADIUS,
                                               object_type=proj.object_type)
        self.factory.ctx.physics.projectiles.remove(proj)

    def on_impact_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        """Triggered when a projectile hits an actor."""
        char_actor = self.factory.ctx.characters.actors.get_by_id(phys_actor.object_id)
        if char_actor is not None:
            self.factory.characters.apply_projectile_hit(char_actor, 2, proj)

        # drop projectile as object
        self.factory.ctx.physics.create_object(x=proj.pos.x, y=proj.pos.y - constants.OBJECT_RADIUS,
                                               object_type=proj.object_type)

        self.factory.ctx.physics.projectiles.remove(proj)

    def on_touch_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        """Triggered when an actor touches another actor."""
        pass

    # --- Animation Events -

    def on_climb(self, ani: animations.Actor) -> None:
        pass

    def on_step(self, ani: animations.Actor) -> None:
        pass

    def on_attack(self, ani: animations.Actor) -> None:
        """Triggered when an attack animation finished."""
        actor = self.factory.ctx.characters.actors.get_by_id(ani.object_id)
        if actor is None:
            return

        victims = characters.query_melee_range(actor, self.factory.ctx.characters, self.factory.ctx.physics)
        for victim in victims:
            characters.attack_enemy(1, victim)
            if victim.hit_points == 0:
                self.on_char_died(victim, 1, actor)
            else:
                self.on_char_damaged(victim, 1, actor)

    def on_throw(self, ani_actor: animations.Actor) -> None:
        """Triggered when an attack animation finished."""
        actor = self.factory.ctx.characters.actors.get_by_id(ani_actor.object_id)
        proj = characters.throw_object(actor, 3.0, constants.ObjectType.WEAPON, self.factory.ctx.physics,
                                       self.factiry.create_projectile)
        proj.move.force.y = 1.0

    def on_died(self, ani_actor: animations.Actor) -> None:
        """Triggered when a dying animation finished."""
        pass

    # --- Character events

    def on_char_damaged(self, actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor got damaged."""
        pass

    def on_char_died(self, char_actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor died. An optional cause can be provided."""
        ani_actor = self.factory.ctx.animations.actors.get_by_id(char_actor.object_id)
        ani_actor.frame.start(animations.Action.DIE)

        phys_actor = self.factory.ctx.physics.actors.get_by_id(char_actor.object_id)
        phys_actor.force_x = 0.0
        phys_actor.can_collide = False
