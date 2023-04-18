import pygame
from dataclasses import dataclass, field

from core import objectids
from platformer import physics, animations

from . import binding


@dataclass
class Actor:
    object_id: int

    keys: binding.Keybinding = field(default_factory=binding.Keybinding)
    state: binding.InputState = field(default_factory=binding.InputState)

    def process_event(self, event: pygame.event.Event) -> None:
        self.state.process_event_action(self.keys, event)
        self.state.process_event_movement(self.keys, event)

    def update(self, elapsed_ms: int) -> None:
        self.state.update(elapsed_ms)

# ----------------------------------------------------------------------------------------------------------------------


class Context:
    def __init__(self):
        self.actors = objectids.IdList[Actor]()

    def create_actor(self, object_id: int) -> Actor:
        actor = Actor(object_id=object_id)
        self.actors.append(actor)
        return actor


# ----------------------------------------------------------------------------------------------------------------------


class ControlsSystem:
    def __init__(self, context: Context, physics_context: physics.Context, animations_context: animations.Context):
        self.context = context
        self.physics_context = physics_context
        self.animations_context = animations_context

    def process_event(self, event: pygame.event.Event) -> None:
        for actor in self.context.actors:
            actor.process_event_action(event)

    def apply_input(self, actor: Actor) -> None:
        # stop if actor is in DIE or LANDING animations, which cannot be skipped
        ani_actor = self.animations_context.actors.get_by_id(actor.object_id)
        if ani_actor.action in animations.BLOCKING_ANIMATIONS:
            return

        # create animation action from input state and the fact whether on a ladder or not
        phys_actor = self.physics_context.actors.get_by_id(actor.object_id)
        is_on_ladder = phys_actor.on_ladder is not None
        is_on_platform = phys_actor.on_platform is not None
        ani_action = actor.state.to_animation(is_on_ladder, is_on_platform)

        # release ladder on case of jumping
        if ani_action == animations.Action.JUMP:
            phys_actor.on_ladder = None

        # prevent "jumping downwards"
        if not is_on_ladder and actor.state.delta.y < 0.0:
            actor.state.delta.y = 0.0

        # apply movement vector as force (y-force is only applied if provided and if not falling)
        phys_actor.move.force.x = actor.state.delta.x
        if actor.state.delta.y != 0.0:
            phys_actor.move.force.y = actor.state.delta.y

    def update(self, elapsed_ms: int) -> None:
        for actor in self.context.actors:
            actor.update(elapsed_ms)
            self.apply_input(actor)
            actor.state.reset()
