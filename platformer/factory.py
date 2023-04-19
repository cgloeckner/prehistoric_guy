import pygame
import random
from typing import Optional

from core import constants, resources, objectids

from . import physics, animations, renderer, characters, controls, interface


class EventListener(physics.EventListener, animations.EventListener, characters.EventListener):
    pass


class MainContext:
    def __init__(self):
        self.id_generator = objectids.object_id_generator()
        self.physics = physics.Context()
        self.animations = animations.Context()
        self.renderer = renderer.Context()
        self.characters = characters.Context()
        self.players = controls.PlayersContext()
        self.enemies = controls.EnemiesContext()


# ----------------------------------------------------------------------------------------------------------------------


class Factory:
    """Factory for creating game objects. Creation and deletion of objects considers all relevant systems."""
    def __init__(self, listener: EventListener, cache: resources.Cache, target: pygame.Surface):
        self.ctx = MainContext()

        self.physics = physics.System(listener, self.ctx.physics)
        self.animation = animations.AnimationSystem(listener, self.ctx.animations, self.ctx.physics)
        self.camera = renderer.Camera(*target.get_size())
        self.renderer = renderer.Renderer(self.camera, target, self.ctx.physics, self.ctx.animations,
                                          self.ctx.renderer, cache)
        self.characters = characters.CharacterSystem(listener, self.ctx.characters, self.ctx.animations)
        self.players = controls.PlayersSystem(self.ctx.players, self.ctx.physics, self.ctx.animations)
        self.enemies = controls.EnemiesSystem(self.ctx.enemies, self.ctx.physics, self.ctx.animations,
                                              self.ctx.characters)
        self.huds = interface.HudSystem(self.ctx.players, self.ctx.physics, self.ctx.characters, target, cache,
                                        self.camera)

    def create_random_object(self) -> None:
        # pick random position on random platform
        p = random.choice(self.ctx.physics.platforms)
        x = random.randrange(p.width)

        self.ctx.physics.create_object(x=p.pos.x + x, y=p.pos.y + 0.5,
                                           object_type=random.choice(list(constants.ObjectType)))

    def create_projectile(self, x: float, y: float, from_actor: Optional[physics.Actor], speed: float,
                          object_type: constants.ObjectType) -> physics.Projectile:
        object_id = next(self.ctx.id_generator)
        physics_proj = self.ctx.physics.create_projectile(object_id=object_id, x=x, y=y, from_actor=from_actor,
                                                              object_type=object_type)
        physics_proj.move.speed = speed
        animations_proj = self.ctx.animations.create_projectile(object_id=object_id)

        return physics_proj

    def create_actor(self, sprite_sheet: pygame.Surface, **kwargs) -> int:
        """Create an actor object such as player or enemy characters. Returns the object id."""
        object_id = next(self.ctx.id_generator)

        kwargs['object_id'] = object_id
        phys_actor = self.ctx.physics.create_actor(**kwargs)
        ani_actor = animations.Actor(object_id=object_id)
        render_actor = renderer.Actor(object_id=object_id, sprite_sheet=sprite_sheet)

        self.ctx.animations.actors.append(ani_actor)
        self.ctx.renderer.actors.append(render_actor)

        return object_id

    def destroy_actor_by_id(self, object_id: int) -> None:
        """Remove an actor (with all components) using the object id."""
        phys_actor = self.ctx.physics.actors.get_by_id(object_id)
        ani_actor = self.ctx.animations.actors.get_by_id(object_id)
        render_actor = self.ctx.renderer.actors.get_by_id(object_id)
        self.ctx.physics.actors.remove(phys_actor)
        self.ctx.animations.actors.remove(ani_actor)
        self.ctx.renderer.actors.remove(render_actor)

    def create_character(self, sprite_sheet: pygame.Surface, x: float, y: float, max_hit_points: int, num_axes: int) \
            -> characters.Actor:
        """Creates and returns a character """
        object_id = self.create_actor(sprite_sheet, x=x, y=y)
        character = self.ctx.characters.create_actor(object_id, max_hit_points=max_hit_points,
                                                         num_axes=num_axes)
        return character

    def destroy_character(self, character: characters.Actor, keep_components: bool = False) -> None:
        """Remove a character. If keep_components is True, the underlying actor remains intact."""
        if keep_components:
            # stop movement and make unable to collide anymore
            phys_actor = self.ctx.physics.actors.get_by_id(character.object_id)
            phys_actor.force_x = 0.0
            phys_actor.can_collide = False
        else:
            # remove other actor components
            self.destroy_actor_by_id(character.object_id)
        self.ctx.characters.actors.remove(character)

    def create_player(self, character: characters.Actor, keys: controls.Keybinding) -> controls.Player:
        """Create a player for an existing character actor. Returns the player actor."""
        actor = self.ctx.players.create_actor(character.object_id)
        actor.keys = keys
        return actor

    def create_enemy(self, sprite_sheet: pygame.Surface, x: float, y: float, max_hit_points: int, num_axes: int) \
            -> characters.Actor:
        enemy_char = self.create_character(sprite_sheet, x, y, max_hit_points, num_axes)
        self.ctx.enemies.create_actor(enemy_char.object_id)

        return enemy_char

    def destroy_enemy(self, character: characters.Actor, keep_components: bool = False) -> None:
        enemy = self.ctx.enemies.actors.get_by_id(character.object_id)
        if enemy is not None:
            self.ctx.enemies.actors.remove()
        self.destroy_character(character, keep_components)

    def update(self, elapsed_ms: int) -> None:
        """Update all related systems."""
        self.physics.update(elapsed_ms)
        self.animation.update(elapsed_ms)
        self.renderer.update(elapsed_ms)
        self.characters.update(elapsed_ms)
        self.players.update(elapsed_ms)
        self.enemies.update(elapsed_ms)

    def draw(self) -> None:
        """Draw scene and HUD."""
        self.renderer.draw()
        self.huds.draw()
