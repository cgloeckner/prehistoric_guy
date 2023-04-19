import pygame

from . import platforms, ladders, actors, projectiles
from .context import EventListener, Context


class ActorSystem(object):
    """Handles updating all actors."""

    def __init__(self, listener: EventListener, context: Context):
        self.listener = listener
        self.context = context

    def handle_ladders(self, actor: actors.Actor) -> None:
        """Handles grabbing and releasing a ladder."""
        if actor.on_ladder is None:
            ladder = ladders.get_closest_ladder_in_reach(actor.pos, self.context.ladders)
            if ladder is not None:
                actor.on_ladder = ladder
                self.listener.on_grab(actor)

        # leaving ladder?
        if actor.on_ladder is not None:
            if not actor.on_ladder.is_in_reach_of(actor.pos):
                # reached end of ladder
                actor.on_ladder = None
                self.listener.on_release(actor)

    def handle_gravity(self, actor: actors.Actor, elapsed_ms: int) -> None:
        """Handles gravity simulation."""
        if not actor.can_fall():
            return

        starts_falling = actor.move.apply_gravity(elapsed_ms)
        if starts_falling:
            self.listener.on_falling(actor)

    def handle_movement(self, actor: actors.Actor, elapsed_ms: int) -> pygame.math.Vector2:
        """Handles movement and jumping off a ladder. Returns the previous position."""
        has_ladder = actor.on_ladder is not None
        old_pos = actor.move.apply_movement(actor.pos, elapsed_ms, has_ladder=has_ladder)

        # moving off the ladder?
        if has_ladder:
            if actor.move.force.x != 0.0:
                actor.on_ladder = None
                self.listener.on_release(actor)
            else:
                actor.move.force.y = 0.0

        return old_pos

    def handle_landing(self, actor: actors.Actor, old_pos: pygame.math.Vector2) -> None:
        """Handles landing on a platform."""
        has_reloaded_support_platform = False

        platform = platforms.get_landing_platform(old_pos, actor.pos, self.context.platforms)
        if platform is not None:
            actor.land_on_platform(platform, old_pos)
            has_reloaded_support_platform = True
            self.listener.on_landing(actor)

        if not has_reloaded_support_platform:
            actor.on_platform = platforms.get_support_platform(actor.pos, self.context.platforms)

    def handle_platform_collision(self, actor: actors.Actor, old_pos: pygame.math.Vector2) -> None:
        """Handles collision with platforms."""
        # platform collision
        platform = platforms.get_platform_collision(actor.pos, self.context.platforms)
        if platform is not None:
            actor.collide_with_platform(platform, old_pos)
            self.listener.on_collision(actor, platform)

    def handle_object_collision(self, actor: actors.Actor) -> None:
        """Finds and reports collisions between the actor and all relevant objects."""
        circ1 = actor.get_circ()
        for obj in self.context.objects:
            circ2 = obj.get_circ()
            if circ1.collidecirc(circ2):
                self.listener.on_touch_object(actor, obj)

    def handle_actor_collision(self, actor: actors.Actor) -> None:
        """Finds and reports collisions between the actor and all relevant actors."""
        circ1 = actor.get_circ()
        for other in self.context.actors:
            if actor == other:
                continue
            circ2 = other.get_circ()
            if circ1.collidecirc(circ2):
                self.listener.on_touch_actor(actor, other)

    def update(self, elapsed_ms: int) -> None:
        for actor in self.context.actors:
            self.handle_ladders(actor)
            self.handle_gravity(actor, elapsed_ms)
            old_pos = self.handle_movement(actor, elapsed_ms)

            if actor.on_ladder is None:
                self.handle_landing(actor, old_pos)
                self.handle_platform_collision(actor, old_pos)

            self.handle_object_collision(actor)
            self.handle_actor_collision(actor)


# ----------------------------------------------------------------------------------------------------------------------

class ProjectileSystem(object):
    """Handles updating all projectiles."""

    def __init__(self, listener: EventListener, context: Context):
        self.listener = listener
        self.context = context

    @staticmethod
    def handle_movement(projectile: projectiles.Projectile, elapsed_ms: int) -> pygame.math.Vector2:
        """Handles gravity and movement, updating the projectile's position in place.
        Returns the previous position.
        """
        projectile.move.apply_gravity(elapsed_ms)
        old_pos = projectile.move.apply_movement(projectile.pos, elapsed_ms,
                                                     gravity_weight=projectiles.GRAVITY_WEIGHT)
        return old_pos

    def handle_platform_collision(self, projectile: projectiles.Projectile, old_pos: pygame.math.Vector2) -> None:
        """Checks for platform collision, both from above and x-wise."""
        platform = platforms.get_landing_platform(old_pos, projectile.pos, self.context.platforms)
        if platform is not None:
            projectile.land_on_platform(platform, old_pos)
            self.listener.on_impact_platform(projectile, platform)

        platform = platforms.get_platform_collision(projectile.pos, self.context.platforms)
        if platform is not None:
            projectile.collide_with_platform(old_pos)
            self.listener.on_impact_platform(projectile, platform)

    def handle_actor_collision(self, projectile: projectiles.Projectile) -> None:
        """Finds and reports collisions between the projectile and all relevant actors."""
        circ1 = projectile.get_circ()
        for actor in self.context.actors:
            if not projectile.can_hit(actor):
                continue
            circ2 = actor.get_circ()
            if circ1.collidecirc(circ2):
                self.listener.on_impact_actor(projectile, actor)
                projectile.move.force.x = 0.0

    def update(self, elapsed_ms: int) -> None:
        for projectile in self.context.projectiles:
            old_pos = self.handle_movement(projectile, elapsed_ms)
            self.handle_platform_collision(projectile, old_pos)
            self.handle_actor_collision(projectile)


# ----------------------------------------------------------------------------------------------------------------------


class System:
    def __init__(self, listener: EventListener, context: Context):
        self.actor_system = ActorSystem(listener, context)
        self.projectile_system = ProjectileSystem(listener, context)

    def update(self, elapsed_ms: int) -> None:
        self.actor_system.update(elapsed_ms)
        self.projectile_system.update(elapsed_ms)
