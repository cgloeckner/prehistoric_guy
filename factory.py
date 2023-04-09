import pygame

import platforms
import animations
import tiles
import controls


class ObjectManager(object):
    """Factory for creating game objects.
    Creation and deletion of objects considers all relevant systems.
    """
    def __init__(self, physics: platforms.Physics, animation: animations.Animating, renderer: tiles.Renderer):
        """Register all known systems that deal with game objects of any kind.
        """
        self.next_obj_id = 0
        self.physics = physics
        self.animation = animation
        self.renderer = renderer

        self.characters = list()

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

    def create_ladder(self, **kwargs) -> platforms.Ladder:
        """Create a new ladder.
        """
        ladder = platforms.Ladder(**kwargs)
        self.physics.ladders.append(ladder)
        # NOTE: The renderer grabs ladders from the physics system.
        return ladder

    def destroy_ladder(self, ladder: platforms.Ladder) -> None:
        """Remove an existing ladder.
        """
        self.physics.ladders.remove(ladder)

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

    def create_projectile(self, **kwargs) -> platforms.Projectile:
        """Create a projectile e.g. a thrown weapon.
        """
        proj = platforms.Projectile(**kwargs)
        self.physics.projectiles.append(proj)
        # NOTE: The renderer grabs objects from the physics system.
        return proj

    def destroy_projectile(self, proj: platforms.Projectile) -> None:
        """Remove an existing projectile."""
        self.physics.projectiles.remove(proj)

    def create_sprite(self, sprite_sheet: pygame.Surface, **kwargs) -> tiles.Sprite:
        """Create an actor sprite object such as player or enemy characters.
        Returns a sprite which links to the actor and its animations.
        """
        actor = platforms.Actor(id=self.next_obj_id, **kwargs)
        animation = animations.Animation(id=self.next_obj_id)

        sprite = tiles.Sprite(sprite_sheet=sprite_sheet, actor=actor, animation=animation)
        self.physics.actors.append(actor)
        self.animation.animations.append(animation)
        self.renderer.sprites.append(sprite)

        self.next_obj_id += 1

        return sprite

    def destroy_sprite(self, sprite: tiles.Sprite) -> None:
        """Remove an actor sprite (as well as its animation) from by using the related sprite object.
        """
        self.physics.actors.remove(sprite.actor)
        self.animation.animations.remove(sprite.animation)
        self.renderer.sprites.remove(sprite)

    def create_character(self, **kwargs) -> controls.Character:
        """Create a character.
        Returns the character
        """
        sprite = self.create_sprite(**kwargs)
        character = controls.Character(sprite)
        self.characters.append(character)

        return character

    def destroy_character(self, character: controls.Character) -> None:
        """Remove a character.
        """
        self.destroy_sprite(character.sprite)
        self.characters.remove(character)
