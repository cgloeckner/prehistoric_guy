import pygame
import random
from typing import Optional

from core import constants, resources, objectids

from . import physics, animations, renderer, characters, players


class ObjectManager(physics.EventListener, animations.EventListener, characters.EventListener):
    """Factory for creating game objects. Creation and deletion of objects considers all relevant systems."""
    def __init__(self, cache: resources.Cache, target: pygame.Surface):
        self.id_generator = objectids.object_id_generator()
        self.physics_context = physics.Context()
        self.physics = physics.System(self, self.physics_context)
        self.animations_context = animations.Context()
        self.animation = animations.AnimationSystem(self, self.animations_context, self.physics_context)
        self.camera = renderer.Camera(*target.get_size())
        self.renderer_context = renderer.Context()
        self.renderer = renderer.Renderer(self.camera, target, self.physics_context, self.animations_context,
                                          self.renderer_context, cache)
        self.characters_context = characters.Context()
        self.characters = characters.CharacterSystem(self, self.characters_context, self.animations_context)
        self.controls_context = players.Context()
        self.controls = players.ControlsSystem(self.controls_context, self.physics_context, self.animations_context)
        self.huds = players.HudSystem(self.controls_context, self.physics_context, self.characters_context, target,
                                      cache, self.camera)

    def create_random_object(self) -> None:
        # pick random position on random platform
        p = random.choice(self.physics_context.platforms)
        x = random.randrange(p.width)

        self.physics_context.create_object(x=p.pos.x + x, y=p.pos.y + 0.5,
                                           object_type=random.choice(list(constants.ObjectType)))

    def create_projectile(self, x: float, y: float, from_actor: Optional[physics.Actor], speed: float,
                          object_type: constants.ObjectType) -> physics.Projectile:
        object_id = next(self.id_generator)
        physics_proj = self.physics_context.create_projectile(object_id=object_id, x=x, y=y, from_actor=from_actor,
                                                              object_type=object_type)
        physics_proj.move.speed = speed
        animations_proj = self.animations_context.create_projectile(object_id=object_id)

        return physics_proj

    # --- Physics Events ----------------------------------------------------------------------------------------------

    def on_grab(self, actor: physics.Actor) -> None:
        """Triggered when the actor grabs a ladder."""
        player = self.controls_context.actors.get_by_id(actor.object_id)
        if player is not None:
            return

        # enemy! let 'm climb
        actor.pos.x = actor.on_ladder.pos.x
        actor.move.force.x = 0.0
        actor.move.force.y = 0.0
        ani_enemy = self.animations_context.actors.get_by_id(actor.object_id)
        ani_enemy.frame.start(animations.Action.IDLE)

    def on_release(self, actor: physics.Actor) -> None:
        """Triggered when the actor releases a ladder."""
        pass

    def on_falling(self, phys_actor: physics.Actor) -> None:
        """Triggered when the actor starts falling."""
        actor = self.characters_context.actors.get_by_id(phys_actor.object_id)
        characters.set_falling_from(actor, phys_actor)

    def on_landing(self, phys_actor: physics.Actor) -> None:
        """Triggered when the actor landed on a platform."""
        actor = self.characters_context.actors.get_by_id(phys_actor.object_id)
        action, damage = characters.apply_landing(actor, phys_actor)
        ani_actor = self.animations_context.actors.get_by_id(phys_actor.object_id)

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
        char_actor = self.characters_context.actors.get_by_id(phys_actor.object_id)
        if char_actor is not None:
            if obj.object_type == constants.ObjectType.FOOD:
                # heal him
                char_actor.hit_points += 1
                # FIXME: on_player_healed

            elif obj.object_type == constants.ObjectType.WEAPON:
                # grab axe
                char_actor.num_axes += 1
                # FIXME: on_weapon_collected

        self.physics_context.objects.remove(obj)
        self.create_random_object()

    def on_impact_platform(self, proj: physics.Projectile, platform: physics.Platform) -> None:
        """Triggered when a projectile hits a platform."""
        self.physics_context.create_object(x=proj.pos.x, y=proj.pos.y - constants.OBJECT_RADIUS,
                                           object_type=proj.object_type)
        self.physics_context.projectiles.remove(proj)

    def on_impact_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        """Triggered when a projectile hits an actor."""
        char_actor = self.characters_context.actors.get_by_id(phys_actor.object_id)
        if char_actor is not None:
            self.characters.apply_projectile_hit(char_actor, 2, proj)

        # drop projectile as object
        self.physics_context.create_object(x=proj.pos.x, y=proj.pos.y - constants.OBJECT_RADIUS,
                                           object_type=proj.object_type)

        self.physics_context.projectiles.remove(proj)

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
        actor = self.characters_context.actors.get_by_id(ani.object_id)
        if actor is None:
            return

        victims = characters.query_melee_range(actor, self.characters_context, self.physics_context)
        for victim in victims:
            characters.attack_enemy(1, victim)
            if victim.hit_points == 0:
                self.on_char_died(victim, 1, actor)
            else:
                self.on_char_damaged(victim, 1, actor)

    def on_throw(self, ani_actor: animations.Actor) -> None:
        """Triggered when an attack animation finished."""
        actor = self.characters_context.actors.get_by_id(ani_actor.object_id)
        proj = characters.throw_object(actor, 3.0, constants.ObjectType.WEAPON, self.physics_context,
                                       self.create_projectile)
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
        ani_actor = self.animations_context.actors.get_by_id(char_actor.object_id)
        ani_actor.frame.start(animations.Action.DIE)

        phys_actor = self.physics_context.actors.get_by_id(char_actor.object_id)
        phys_actor.force_x = 0.0
        phys_actor.can_collide = False

    # --- Factory methods

    def create_actor(self, sprite_sheet: pygame.Surface, **kwargs) -> int:
        """Create an actor object such as player or enemy characters. Returns the object id."""
        object_id = next(self.id_generator)

        kwargs['object_id'] = object_id
        phys_actor = self.physics_context.create_actor(**kwargs)
        ani_actor = animations.Actor(object_id=object_id)
        render_actor = renderer.Actor(object_id=object_id, sprite_sheet=sprite_sheet)

        self.animations_context.actors.append(ani_actor)
        self.renderer_context.actors.append(render_actor)

        return object_id

    def destroy_actor_by_id(self, object_id: int) -> None:
        """Remove an actor (with all components) using the object id."""
        phys_actor = self.physics_context.actors.get_by_id(object_id)
        ani_actor = self.animations_context.actors.get_by_id(object_id)
        render_actor = self.renderer_context.actors.get_by_id(object_id)
        self.physics_context.actors.remove(phys_actor)
        self.animations_context.actors.remove(ani_actor)
        self.renderer_context.actors.remove(render_actor)

    def create_character(self, sprite_sheet: pygame.Surface, x: float, y: float, max_hit_points: int, num_axes: int) \
            -> characters.Actor:
        """Creates and returns a character """
        object_id = self.create_actor(sprite_sheet, x=x, y=y)
        character = self.characters_context.create_actor(object_id, max_hit_points=max_hit_points,
                                                         num_axes=num_axes)
        return character

    def destroy_character(self, character: characters.Actor, keep_components: bool = False) -> None:
        """Remove a character. If keep_components is True, the underlying actor remains intact."""
        if keep_components:
            # stop movement and make unable to collide anymore
            phys_actor = self.physics_context.actors.get_by_id(character.object_id)
            phys_actor.force_x = 0.0
            phys_actor.can_collide = False
        else:
            # remove other actor components
            self.destroy_actor_by_id(character.object_id)
        self.characters_context.actors.remove(character)

    def create_player(self, character: characters.Actor, **kwargs) -> players.Actor:
        """Create a player for an existing character actor. Returns the player actor."""
        actor = self.controls_context.create_actor(character.object_id)
        return actor

    def update(self, elapsed_ms: int) -> None:
        """Update all related systems."""
        self.physics.update(elapsed_ms)
        self.animation.update(elapsed_ms)
        self.renderer.update(elapsed_ms)
        self.characters.update(elapsed_ms)
        self.controls.update(elapsed_ms)

    def draw(self) -> None:
        """Draw scene and HUD."""
        self.renderer.draw()
        self.huds.draw()
