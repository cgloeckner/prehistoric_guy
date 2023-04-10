import pygame

import platformer.physics as physics
import platformer.animations as animations
import platformer.render as render
import platformer.controls as controls


class ObjectManager(object):
    """Factory for creating game objects.
    Creation and deletion of objects considers all relevant systems.
    """
    def __init__(self, physics: physics.Physics, animation: animations.Animating, renderer: render.Renderer):
        """Register all known systems that deal with game objects of any kind.
        """
        self.next_obj_id = 0
        self.physics = physics
        self.animation = animation
        self.renderer = renderer

        self.characters = list()

    def create_platform(self, **kwargs) -> physics.Platform:
        """Create a new platform.
        """
        platform = physics.Platform(**kwargs)
        self.physics.platforms.append(platform)
        # NOTE: The renderer grabs platforms from the physics system.
        return platform

    def destroy_platform(self, platform: physics.Platform) -> None:
        """Remove an existing platform.
        """
        self.physics.platforms.remove(platform)

    def create_ladder(self, **kwargs) -> physics.Ladder:
        """Create a new ladder.
        """
        ladder = physics.Ladder(**kwargs)
        self.physics.ladders.append(ladder)
        # NOTE: The renderer grabs ladders from the physics system.
        return ladder

    def destroy_ladder(self, ladder: physics.Ladder) -> None:
        """Remove an existing ladder.
        """
        self.physics.ladders.remove(ladder)

    def create_object(self, **kwargs) -> physics.Object:
        """Create a static object such as fireplaces or powerups.
        """
        obj = physics.Object(**kwargs)
        self.physics.objects.append(obj)
        # NOTE: The renderer grabs objects from the physics system.
        return obj

    def destroy_object(self, obj: physics.Object) -> None:
        """Remove an existing, static object."""
        self.physics.objects.remove(obj)

    def create_projectile(self, **kwargs) -> physics.Projectile:
        """Create a projectile e.g. a thrown weapon.
        """
        proj = physics.Projectile(**kwargs)
        self.physics.projectiles.append(proj)
        # NOTE: The renderer grabs objects from the physics system.
        return proj

    def destroy_projectile(self, proj: physics.Projectile) -> None:
        """Remove an existing projectile."""
        self.physics.projectiles.remove(proj)

    def create_sprite(self, sprite_sheet: pygame.Surface, **kwargs) -> render.Sprite:
        """Create an actor sprite object such as player or enemy characters.
        Returns a sprite which links to the actor and its animations.
        """
        actor = physics.Actor(id=self.next_obj_id, **kwargs)
        animation = animations.Animation(id=self.next_obj_id)

        sprite = render.Sprite(sprite_sheet=sprite_sheet, actor=actor, animation=animation)
        self.physics.actors.append(actor)
        self.animation.animations.append(animation)
        self.renderer.sprites.append(sprite)

        self.next_obj_id += 1

        return sprite

    def destroy_sprite(self, sprite: render.Sprite) -> None:
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
