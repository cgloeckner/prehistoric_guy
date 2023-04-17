import pygame
import random
from typing import Optional

from core import constants, resources

from . import physics, animations, renderer, characters, players


class ObjectManager(physics.EventListener, animations.EventListener, characters.EventListener):
    """Factory for creating game objects. Creation and deletion of objects considers all relevant systems."""
    def __init__(self, cache: resources.Cache, target: pygame.Surface):
        self.next_obj_id = 0
        self.physics_context = physics.Context()
        self.physics = physics.System(self, self.physics_context)
        self.animations_context = animations.Context()
        self.animation = animations.Animating(self, self.animations_context)
        self.camera = renderer.Camera(*target.get_size())
        self.renderer_context = renderer.Context()
        self.renderer = renderer.ImageRenderer(self.camera, target, self.physics_context, self.animations_context,
                                               self.renderer_context, cache)
        self.chars = characters.Characters(self)
        self.players = players.Players(self.physics_context, self.animations_context, self.renderer_context,
                                       self.chars, cache, target)

    def create_random_object(self) -> None:
        # pick random position on random platform
        p = random.choice(self.physics_context.platforms)
        x = random.randrange(p.width)

        self.create_object(x=p.pos.x + x, y=p.pos.y + 0.5, object_type=random.choice(list(constants.ObjectType)))

    # --- Physics Events ----------------------------------------------------------------------------------------------

    def on_grab(self, actor: physics.Actor) -> None:
        """Triggered when the actor grabs a ladder."""
        pass

    def on_release(self, actor: physics.Actor) -> None:
        """Triggered when the actor releases a ladder."""
        pass

    def on_falling(self, actor: physics.Actor) -> None:
        """Triggered when the actor starts falling."""
        pass

    def on_landing(self, phys_actor: physics.Actor) -> None:
        """Triggered when the actor landed on a platform."""
        ani_actor = self.animation.get_actor_by_id(phys_actor.object_id)
        action = animations.Action.IDLE

        char_actor = self.chars.try_get_by_id(phys_actor.object_id)
        if char_actor is None:
            # go to IDLE
            animations.start(ani_actor, action)
            return

        return
        # FIXME: not implemented yet
        #char_actor = self.chars.get_by_id(phys_actor.object_id)
        #delta_h = phys_actor.fall_from_y - phys_actor.y
        #
        #if delta_h > characters.DANGEROUS_HEIGHT:
        #    action = animations.Action.LANDING
        #
        #animations.start(ani_actor, action)
        #
        #damage = characters.get_falling_damage(delta_h)
        #if damage > 0:
        #    self.chars.apply_damage(char_actor, damage)

    def on_collision(self, actor: physics.Actor, platform: physics.Platform) -> None:
        """Triggered when the actor runs into a platform."""
        pass

    def on_touch_object(self, phys_actor: physics.Actor, obj: physics.Object) -> None:
        """Triggered when the actor reaches an object."""
        char_actor = self.chars.try_get_by_id(phys_actor.object_id)
        if char_actor is not None:
            if obj.object_type == constants.ObjectType.FOOD:
                # heal him
                char_actor.hit_points += 1
                # FIXME: on_player_healed

            elif obj.object_type == constants.ObjectType.WEAPON:
                # grab axe
                char_actor.num_axes += 1
                # FIXME: on_weapon_collected

        self.destroy_object(obj)
        self.create_random_object()

    def on_impact_platform(self, proj: physics.Projectile, platform: physics.Platform) -> None:
        """Triggered when a projectile hits a platform."""
        self.create_object(x=proj.pos.x, y=proj.pos.y - constants.OBJECT_RADIUS, object_type=proj.object_type)
        self.destroy_projectile(proj)

    def on_impact_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        """Triggered when a projectile hits an actor."""
        char_actor = self.chars.try_get_by_id(phys_actor.object_id)
        if char_actor is not None:
            self.chars.apply_projectile_hit(char_actor, 2, proj)

        # drop projectile as object
        self.create_object(x=proj.pos.x, y=proj.pos.y - constants.OBJECT_RADIUS, object_type=proj.object_type)

        self.destroy_projectile(proj)

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
        char_actor = self.chars.try_get_by_id(ani.object_id)
        if char_actor is None:
            return

        # query target actors
        phys_actor = self.physics_context.get_actor_by_id(ani.object_id)
        targets = phys_actor.get_all_faced_actors(self.physics_context.actors, characters.MELEE_ATTACK_RADIUS)

        # damage their characters if possible
        for other in targets:
            other_char = self.chars.try_get_by_id(other.object_id)
            if other_char is None:
                continue

            self.chars.apply_damage(other_char, 1, char_actor)

    def on_throw(self, ani_actor: animations.Actor) -> None:
        """Triggered when an attack animation finished."""
        char_actor = self.chars.get_by_id(ani_actor.object_id)
        phys_actor = self.physics_context.get_actor_by_id(ani_actor.object_id)
        if char_actor.num_axes == 0:
            return

        char_actor.num_axes -= 1
        proj = self.create_projectile(x=phys_actor.pos.x, y=phys_actor.pos.y + phys_actor.radius, from_actor=phys_actor)
        proj.movement.face_x = phys_actor.move.face_x
        proj.movement.force.x = phys_actor.move.face_x
        proj.movement.force.y = 0.5
        proj.movement.speed = 4.0

    def on_died(self, ani_actor: animations.Actor) -> None:
        """Triggered when a dying animation finished."""
        pass

    # --- Character events

    def on_char_damaged(self, actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor got damaged."""
        ani_actor = self.animation.get_actor_by_id(actor.object_id)
        animations.flash(ani_actor, resources.HslTransform(lightness=100), 200)

    def on_char_died(self, char_actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor died. An optional cause can be provided."""
        ani_actor = self.animation.get_actor_by_id(char_actor.object_id)
        animations.start(ani_actor, animations.Action.DIE)
        self.destroy_character(char_actor, keep_components=True)

    # --- Factory methods

    # FIXME: remove if inside context (and add destroy_* to context)

    def create_platform(self, **kwargs) -> physics.Platform:
        """Create a new platform."""
        platform = self.physics_context.create_platform(**kwargs)
        # NOTE: The renderer grabs platforms from the physics system.
        return platform

    def destroy_platform(self, platform: physics.Platform) -> None:
        """Remove an existing platform."""
        self.physics_context.platforms.remove(platform)

    def create_ladder(self, **kwargs) -> physics.Ladder:
        """Create a new ladder."""
        ladder = self.physics_context.create_ladder(**kwargs)
        # NOTE: The renderer grabs ladders from the physics system.
        return ladder

    def destroy_ladder(self, ladder: physics.Ladder) -> None:
        """Remove an existing ladder."""
        self.physics_context.ladders.remove(ladder)

    def create_object(self, **kwargs) -> physics.Object:
        """Create a static object such as fireplaces or powerups."""
        obj = self.physics_context.create_object(**kwargs)
        # NOTE: The renderer grabs objects from the physics system.
        return obj

    def destroy_object(self, obj: physics.Object) -> None:
        """Remove an existing, static object."""
        self.physics_context.objects.remove(obj)

    def create_projectile(self, **kwargs) -> physics.Projectile:
        """Create a projectile e.g. a thrown weapon."""
        proj = self.physics_context.create_projectile(**kwargs)
        # NOTE: The renderer grabs objects from the physics system.
        return proj

    def destroy_projectile(self, proj: physics.Projectile) -> None:
        """Remove an existing projectile."""
        self.physics_context.projectiles.remove(proj)

    def create_actor(self, sprite_sheet: pygame.Surface, **kwargs) -> int:
        """Create an actor object such as player or enemy characters. Returns the object id."""
        object_id = self.next_obj_id
        self.next_obj_id += 1

        kwargs['object_id'] = object_id
        phys_actor = self.physics_context.create_actor(**kwargs)
        ani_actor = animations.Actor(object_id=object_id)
        render_actor = renderer.Actor(object_id=object_id, sprite_sheet=sprite_sheet)

        self.animation.context.actors.append(ani_actor)
        self.renderer.sprite_context.actors.append(render_actor)

        return object_id

    def destroy_actor_by_id(self, object_id: int) -> None:
        """Remove an actor (with all components) using the object id."""
        phys_actor = self.physics_context.get_actor_by_id(object_id)
        ani_actor = self.animation.get_actor_by_id(object_id)
        render_actor = self.renderer.sprite_context.get_actor_by_id(object_id)
        self.physics_context.actors.remove(phys_actor)
        self.animation.context.actors.remove(ani_actor)
        self.renderer.sprite_context.actors.remove(render_actor)

    def create_character(self, sprite_sheet: pygame.Surface, **kwargs) -> characters.Actor:
        """Creates and returns a character """
        object_id = self.create_actor(sprite_sheet, **kwargs)
        character = characters.Actor(object_id)
        self.chars.characters.append(character)

        return character

    def destroy_character(self, character: characters.Actor, keep_components: bool = False) -> None:
        """Remove a character. If keep_components is True, the underlying actor remains intact."""
        if keep_components:
            # stop movement and make unable to collide anymore
            phys_actor = self.physics_context.get_actor_by_id(character.object_id)
            phys_actor.force_x = 0.0
            phys_actor.can_collide = False
        else:
            # remove other actor components
            self.destroy_actor_by_id(character.object_id)
        self.chars.characters.remove(character)

    def create_player(self, character: characters.Actor, **kwargs) -> players.Actor:
        """Create a player for an existing character actor. Returns the player actor."""
        player_actor = players.Actor(object_id=character.object_id, **kwargs)
        self.players.players.append(player_actor)
        return player_actor

    def update(self, elapsed_ms: int) -> None:
        """Update all related systems."""
        self.physics.update(elapsed_ms)
        self.animation.update(elapsed_ms)
        self.renderer.update(elapsed_ms)
        self.chars.update(elapsed_ms)
        self.players.update(elapsed_ms)

    def draw(self) -> None:
        # Scene
        self.renderer.draw()

        # HUD
        self.players.draw()

