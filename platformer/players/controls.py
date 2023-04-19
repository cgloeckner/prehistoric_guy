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
            actor.process_event(event)

    def apply_input(self, actor: Actor) -> None:
        phys_actor = self.physics_context.actors.get_by_id(actor.object_id)
        ani_actor = self.animations_context.actors.get_by_id(actor.object_id)

        # get next animation
        is_on_ladder = phys_actor.on_ladder is not None
        is_on_platform = phys_actor.on_platform is not None
        ani_action = actor.state.get_next_animation(is_on_ladder, is_on_platform)

        # verify action
        last_action = ani_actor.frame.action
        ani_action = actor.state.verify_animation(phys_actor, last_action, ani_action)
        if ani_action is None:
            return

        # apply movement vector as force (y-force is only applied if provided and if not falling)
        phys_actor.move.force.x = actor.state.delta.x
        if actor.state.delta.y != 0.0:
            phys_actor.move.force.y = actor.state.delta.y

        # avoid IDLE/HOLD blending over real actions
        if ani_action in [animations.Action.IDLE, animations.Action.HOLD]:
            if ani_actor.frame.action != animations.Action.JUMP:
                return

        # trigger resulting animation action
        ani_actor.frame.start(ani_action)

    def update(self, elapsed_ms: int) -> None:
        for actor in self.context.actors:
            pygame.display.set_caption(str(actor.state))
            actor.update(elapsed_ms)
            self.apply_input(actor)
