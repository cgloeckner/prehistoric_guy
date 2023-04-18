from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from core import objectids

from . import actions, frames, oscillation


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
    def on_step(self, ani: Actor) -> None:
        """Triggered when a cycle of a move animation finished."""
        pass

    @abstractmethod
    def on_climb(self, ani: Actor) -> None:
        """Triggered when a cycle of a climbing animation finished."""
        pass

    @abstractmethod
    def on_attack(self, ani: Actor) -> None:
        """Triggered when an attack animation finished."""
        pass

    @abstractmethod
    def on_throw(self, ani: Actor) -> None:
        """Triggered when a throwing animation finished."""
        pass

    @abstractmethod
    def on_died(self, ani: Actor) -> None:
        """Triggered when a dying animation finished."""
        pass


class AnimationSystem(object):
    """Handles all frame set animations."""
    def __init__(self, animation_listener: EventListener, context: Context):
        self.event_listener = animation_listener
        self.context = context

    def notify_finished(self, ani: Actor) -> None:
        """Notify about a finished animation."""
        if ani.frame.action == actions.Action.MOVE:
            self.event_listener.on_step(ani)
        if ani.frame.action == actions.Action.CLIMB:
            self.event_listener.on_climb(ani)
        elif ani.frame.action == actions.Action.ATTACK:
            self.event_listener.on_attack(ani)
        elif ani.frame.action == actions.Action.THROW:
            self.event_listener.on_throw(ani)
        elif ani.frame.action == actions.Action.DIE:
            self.event_listener.on_died(ani)

    def update_actor(self, actor: Actor, elapsed_ms) -> None:
        """Updates the actor using all related sub-animations."""
        # frame animation
        if actor.frame.step_frame(elapsed_ms):
            self.notify_finished(actor)
            actor.frame.handle_finish()

        # oscillation animation
        actor.oscillate.update(actor.frame.action, elapsed_ms)

    def update(self, elapsed_ms: int) -> None:
        """Updates all animations' frame durations. It automatically switches frames and loops/returns/freezes the
        animation once finished.
        """
        for actor in self.context.actors:
            self.update_actor(actor, elapsed_ms)
