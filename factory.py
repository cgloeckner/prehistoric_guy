import platforms
import animations
import tiles


class ObjectManager(object):
    """Factory for creating game objects.
    Creation and deletion of objects considers all relevant systems.
    """
    def __init__(self, physics: platforms.Physics, animation: animations.Animation, renderer: tiles.Renderer):
        """Register all known systems that deal with game objects of any kind.
        """
        self.physics = physics
        self.animation = animation
        self.renderer = renderer

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

    def create_actor(self, **kwargs) -> platforms.Actor:
        """Create an actor object such as player or enemy characters.
        """
        actor = platforms.Actor(**kwargs)
        self.physics.actors.append(actor)
        # FIXME: introduce sprites for rendering actors in non-debug-mode
        return actor

    def destroy_actor(self, actor: platforms.Actor) -> None:
        self.physics.actors.remove(actor)
        # FIXME: adjust for sprite removal using the rendering system
