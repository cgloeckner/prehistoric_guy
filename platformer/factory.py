import pygame
import random
from typing import Optional

from core import resources

from platformer import camera
from platformer import physics
from platformer import animations
from platformer import render
from platformer import characters
from platformer import players


class ObjectManager(physics.EventListener, animations.EventListener, characters.EventListener):
    """Factory for creating game objects.
    Creation and deletion of objects considers all relevant systems.
    """
    def __init__(self, cache: resources.Cache, target: pygame.Surface):
        self.next_obj_id = 0
        self.context = physics.Context([], [], [], [], [])
        self.physics = physics.System(self, self.context)
        self.animation = animations.Animating(self)
        self.camera = camera.Camera(target)
        self.renderer = render.Renderer(self.context, self.animation, cache, self.camera)
        self.chars = characters.Characters(self)
        self.players = players.Players(self.context, self.animation, self.renderer, self.chars, cache, target)

    def create_random_object(self) -> None:
        # pick random position on random platform
        p = random.choice(self.context.platforms)
        x = random.randrange(p.width)

        self.create_object(pos=pygame.math.Vector2(x=p.pos.x + x, y=p.pos.y + 0.5),
                           object_type=random.randrange(len(physics.ObjectType)))

    # --- Physics Events ----------------------------------------------------------------------------------------------

    def on_falling(self, actor: physics.Actor) -> None:
        """Triggered when the actor starts falling.
        """
        pass

    def on_landing(self, phys_actor: physics.Actor) -> None:
        """Triggered when the actor landed on a platform.
        """
        ani_actor = self.animation.get_by_id(phys_actor.object_id)
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
        """Triggered when the actor runs into a platform.
        """
        pass

    # FIXME: not triggered atm
    #def on_reach_object(self, phys_actor: physics.Actor, obj: physics.Object) -> None:
    #    """Triggered when the actor reaches an object.
    #    """
    #    char_actor = self.chars.try_get_by_id(phys_actor.object_id)
    #    if char_actor is not None:
    #        if obj.object_type == FOOD_OBJ:
    #            # heal him
    #            char_actor.hit_points += 1
    #            # FIXME: on_player_healed
    #
    #        elif obj.object_type == WEAPON_OBJ:
    #            # grab axe
    #            char_actor.num_axes += 1
    #            # FIXME: on_weapon_collected
    #
    #    self.destroy_object(obj)
    #    self.create_random_object()

    # FIXME: not triggered atm
    #def on_impact_platform(self, proj: physics.Projectile, platform: physics.Platform) -> None:
    #    """Triggered when a projectile hits a platform.
    #    """
    #    self.create_object(x=proj.x, y=proj.y - physics.OBJECT_RADIUS, object_type=proj.object_type)
    #    self.destroy_projectile(proj)

    # FIXME: not triggered atm
    #def on_impact_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
    #    """Triggered when a projectile hits an actor.
    #    """
    #    char_actor = self.chars.try_get_by_id(phys_actor.object_id)
    #    if char_actor is not None:
    #        self.chars.apply_projectile_hit(char_actor, 2, proj)
    #
    #    # drop projectile as object
    #    self.create_object(x=proj.x, y=proj.y - physics.OBJECT_RADIUS, object_type=proj.object_type)
    #
    #    self.destroy_projectile(proj)

    # --- Animation Events -

    def on_climb(self, ani: animations.Actor) -> None:
        pass

    def on_step(self, ani: animations.Actor) -> None:
        pass

    def on_attack(self, ani: animations.Actor) -> None:
        """Triggered when an attack animation finished.
        """
        char_actor = self.chars.try_get_by_id(ani.object_id)
        if char_actor is None:
            return

        # query target actors
        phys_actor = self.context.get_by_id(ani.object_id)
        targets = phys_actor.get_all_faced_actors(self.context.actors, characters.MELEE_ATTACK_RADIUS)

        # damage their characters if possible
        for other in targets:
            other_char = self.chars.try_get_by_id(other.object_id)
            if other_char is None:
                continue

            self.chars.apply_damage(other_char, 1, char_actor)

    def on_throw(self, ani_actor: animations.Actor) -> None:
        """Triggered when an attack animation finished.
        """
        char_actor = self.chars.get_by_id(ani_actor.object_id)
        phys_actor = self.context.get_by_id(ani_actor.object_id)
        if char_actor.num_axes == 0:
            return

        char_actor.num_axes -= 1
        proj = self.create_projectile(origin=phys_actor,
                                      pos=pygame.math.Vector2(x=phys_actor.pos.x, y=phys_actor.pos.y + phys_actor.radius),
                                      radius=physics.OBJECT_RADIUS, object_type=physics.ObjectType.WEAPON)
        proj.movement.face_x = phys_actor.movement.face_x

    def on_died(self, ani_actor: animations.Actor) -> None:
        """Triggered when a dying animation finished.
        """
        pass

    # --- Character events

    def on_char_damaged(self, actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor got damaged.
        """
        ani_actor = self.animation.get_by_id(actor.object_id)
        animations.flash(ani_actor, resources.HslTransform(lightness=100), 200)

    def on_char_died(self, char_actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor died. An optional cause can be provided.
        """
        ani_actor = self.animation.get_by_id(char_actor.object_id)
        animations.start(ani_actor, animations.Action.DIE)
        self.destroy_character(char_actor, keep_components=True)

    # --- Factory methods

    def create_platform(self, **kwargs) -> physics.Platform:
        """Create a new platform.
        """
        platform = physics.Platform(**kwargs)
        self.context.platforms.append(platform)
        # NOTE: The renderer grabs platforms from the physics system.
        return platform

    def destroy_platform(self, platform: physics.Platform) -> None:
        """Remove an existing platform.
        """
        self.context.platforms.remove(platform)

    def create_ladder(self, **kwargs) -> physics.Ladder:
        """Create a new ladder.
        """
        ladder = physics.Ladder(**kwargs)
        self.context.ladders.append(ladder)
        # NOTE: The renderer grabs ladders from the physics system.
        return ladder

    def destroy_ladder(self, ladder: physics.Ladder) -> None:
        """Remove an existing ladder.
        """
        self.context.ladders.remove(ladder)

    def create_object(self, **kwargs) -> physics.Object:
        """Create a static object such as fireplaces or powerups.
        """
        obj = physics.Object(**kwargs)
        self.context.objects.append(obj)
        # NOTE: The renderer grabs objects from the physics system.
        return obj

    def destroy_object(self, obj: physics.Object) -> None:
        """Remove an existing, static object."""
        self.context.objects.remove(obj)

    def create_projectile(self, **kwargs) -> physics.Projectile:
        """Create a projectile e.g. a thrown weapon.
        """
        proj = physics.Projectile(**kwargs)
        self.context.projectiles.append(proj)
        # NOTE: The renderer grabs objects from the physics system.
        return proj

    def destroy_projectile(self, proj: physics.Projectile) -> None:
        """Remove an existing projectile."""
        self.context.projectiles.remove(proj)

    def create_actor(self, sprite_sheet: pygame.Surface, **kwargs) -> int:
        """Create an actor object such as player or enemy characters.
        Returns the object id.
        """
        object_id = self.next_obj_id
        self.next_obj_id += 1

        kwargs['object_id'] = object_id
        phys_actor = physics.Actor(**kwargs)
        ani_actor = animations.Actor(object_id=object_id)
        render_actor = render.Actor(object_id=object_id, sprite_sheet=sprite_sheet)

        self.context.actors.append(phys_actor)
        self.animation.animations.append(ani_actor)
        self.renderer.sprites.append(render_actor)

        return object_id

    def destroy_actor_by_id(self, object_id: int) -> None:
        """Remove an actor (with all components) using the object id.
        """
        phys_actor = self.context.get_by_id(object_id)
        ani_actor = self.animation.get_by_id(object_id)
        render_actor = self.renderer.get_by_id(object_id)
        self.context.actors.remove(phys_actor)
        self.animation.animations.remove(ani_actor)
        self.renderer.sprites.remove(render_actor)

    def create_character(self, sprite_sheet: pygame.Surface, **kwargs) -> characters.Actor:
        """Create a character.
        Returns the character
        """
        object_id = self.create_actor(sprite_sheet, **kwargs)
        character = characters.Actor(object_id)
        self.chars.characters.append(character)

        return character

    def destroy_character(self, character: characters.Actor, keep_components: bool = False) -> None:
        """Remove a character.
        If keep_components is True, the underlying actor remains intact.
        """
        if keep_components:
            # stop movement and make unable to collide anymore
            phys_actor = self.context.get_by_id(character.object_id)
            phys_actor.force_x = 0.0
            phys_actor.can_collide = False
        else:
            # remove other actor components
            self.destroy_actor_by_id(character.object_id)
        self.chars.characters.remove(character)

    def create_player(self, character: characters.Actor, **kwargs) -> players.Actor:
        """Create a player for an existing character actor.
        Returns the player actor.
        """
        player_actor = players.Actor(object_id=character.object_id, **kwargs)
        self.players.players.append(player_actor)
        return player_actor

    def update(self, elapsed_ms: int) -> None:
        """Update all related systems.
        """
        self.physics.update(elapsed_ms)
        self.animation.update(elapsed_ms)
        self.renderer.update(elapsed_ms)
        self.chars.update(elapsed_ms)
        self.players.update(elapsed_ms)
        self.camera.update(elapsed_ms)

    def draw(self) -> None:
        # Scene
        self.renderer.draw()
        self.renderer.draw_hitboxes()
        self.camera.draw()

        # HUD
        self.players.draw()

