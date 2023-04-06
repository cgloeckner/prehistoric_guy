import pygame

import platforms
import animations
import tiles


class ObjectManager(object):
    """Factory for creating game objects.
    Creation and deletion of objects considers all relevant systems.
    """
    def __init__(self, physics: platforms.Physics, animation: animations.Animating, renderer: tiles.Renderer):
        """Register all known systems that deal with game objects of any kind.
        """
        self.physics = physics
        self.animation = animation
        self.renderer = renderer

        self.flipped_cache = dict()

    def create_platform(self, **kwargs) -> platforms.Platform:
        """Create a new platform.
        """
        platform = platforms.Platform(**kwargs)
        self.physics.platforms.append(platform)
        # NOTE: The renderer grabs platforms from the physics system.
        return platform

    def destroy_platform(self, platform: platforms.Platform) -> None:
        """Remove an existing platform.
        """
        self.physics.platforms.remove(platform)

    def create_object(self, **kwargs) -> platforms.Object:
        """Create a static object such as fireplaces or powerups.
        """
        obj = platforms.Object(**kwargs)
        self.physics.objects.append(obj)
        # NOTE: The renderer grabs objects from the physics system.
        return obj

    def destroy_object(self, obj: platforms.Object) -> None:
        """Remove an existing, static object."""
        self.physics.objects.remove(obj)

    def create_actor(self, sprite_sheet: pygame.Surface, **kwargs) -> tiles.Sprite:
        """Create an actor object such as player or enemy characters.
        Returns a sprite which links to the actor and its animations.
        """
        if sprite_sheet not in self.flipped_cache:
            self.flipped_cache[sprite_sheet] = animations.flip_sprite_sheet(sprite_sheet, tiles.WORLD_SCALE)
        flipped_sheet = self.flipped_cache[sprite_sheet]

        actor = platforms.Actor(**kwargs)
        animation = animations.Animation()
        # FIXME: bad position to upscale
        sprite = tiles.Sprite(sprite_sheet=pygame.transform.scale2x(sprite_sheet),
                              flipped_sheet=pygame.transform.scale2x(flipped_sheet), actor=actor, animation=animation)
        self.physics.actors.append(actor)
        self.animation.animations.append(animation)
        self.renderer.sprites.append(sprite)
        return sprite

    def destroy_actor(self, sprite: tiles.Sprite) -> None:
        """Remove an actor (as well as its animation) from by using the related sprite object.
        """
        self.physics.actors.remove(sprite.actor)
        self.animation.animations.remove(sprite.animation)
        self.renderer.sprites.remove(sprite)