from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from core import objectids

from . import actions, frames, oscillation, hover
from platformer import physics


@dataclass
class Actor:
    object_id: int
    frame: frames.FrameAnimation = field(default_factory=frames.FrameAnimation)
    oscillate: oscillation.OscillateAnimation = field(default_factory=oscillation.OscillateAnimation)


@dataclass
class Projectile:
    object_id: int
    # FIXME: add stuff for spinning animation


class Context:
    def __init__(self):
        self.actors = objectids.IdList[Actor]()
        self.projectiles = objectids.IdList[Projectile]()

    def create_actor(self, object_id: int) -> Actor:
        a = Actor(object_id=object_id)
        self.actors.append(a)
        return a

    def create_projectile(self, object_id: int) -> Projectile:
        p = Projectile(object_id=object_id)
        self.projectiles.append(p)
        return p

# ----------------------------------------------------------------------------------------------------------------------


class EventListener(ABC):

    @abstractmethod
    def on_animation_finish(self, ani: Actor) -> None:
        """Triggered when a cycle of an animation is finished."""
        pass


class AnimationSystem(object):
    """Handles all frame set animations."""
    def __init__(self, animation_listener: EventListener, context: Context, physics_context: physics.Context):
        self.listener = animation_listener
        self.context = context
        self.physics_context = physics_context

    def notify_finished(self, ani: Actor) -> None:
        """Notify about a finished animation."""
        self.listener.on_animation_finish(ani)

    def handle_allow_climb(self, actor: Actor) -> None:
        """Allowed the physics actor to climb or not, based on the animation.
        """
        physics_actor = self.physics_context.actors.get_by_id(actor.object_id)
        physics_actor.can_climb = actor.frame.action not in actions.BUSY_ANIMATIONS

    def update_actor(self, actor: Actor, elapsed_ms: int) -> None:
        """Updates the actor using all related sub-animations."""
        # frame animation
        if actor.frame.step_frame(elapsed_ms):
            self.notify_finished(actor)
            actor.frame.handle_finish()

        self.handle_allow_climb(actor)

        # oscillation animation
        actor.oscillate.update(actor.frame.action, elapsed_ms)

    def update_platform(self, platform: physics.Platform, elapsed_ms: int) -> None:
        """Updates the platform's hovering."""
        platform.hover.update(elapsed_ms)
        if platform.hover.delta.magnitude_squared() == 0.0:
            # no motion
            return

        platform.pos += platform.hover.delta
        hover.update_actors(platform, self.physics_context.actors)

    def update(self, elapsed_ms: int) -> None:
        """Updates all animations' frame durations. It automatically switches frames and loops/returns/freezes the
        animation once finished.
        """
        for actor in self.context.actors:
            self.update_actor(actor, elapsed_ms)

        for platform in self.physics_context.platforms:
            self.update_platform(platform, elapsed_ms)
