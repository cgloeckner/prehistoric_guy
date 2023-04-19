import pygame
from dataclasses import dataclass, field

from core import objectids
from platformer import physics, animations

from . import binding


@dataclass
class Player:
    object_id: int

    keys: binding.Keybinding = field(default_factory=binding.Keybinding)
    state: binding.InputState = field(default_factory=binding.InputState)

    def process_event(self, event: pygame.event.Event) -> None:
        self.state.process_event(self.keys, event)

    def update(self, elapsed_ms: int, query: binding.KeysQuery) -> None:
        self.state.delta = self.keys.get_movement(query)
        self.state.update_action(elapsed_ms)


# ----------------------------------------------------------------------------------------------------------------------


class PlayersContext:
    def __init__(self):
        self.actors = objectids.IdList[Player]()

        # default key query
        self.query = lambda key: pygame.key.get_pressed()[key]

    def create_actor(self, object_id: int) -> Player:
        actor = Player(object_id=object_id)
        self.actors.append(actor)
        return actor


# ----------------------------------------------------------------------------------------------------------------------


class PlayersSystem:
    def __init__(self, players_context: PlayersContext, physics_context: physics.Context,
                 animations_context: animations.Context):
        self.players_context = players_context
        self.physics_context = physics_context
        self.animations_context = animations_context

    def process_event(self, event: pygame.event.Event) -> None:
        for actor in self.players_context.actors:
            actor.process_event(event)

    def apply_input(self, actor: Player) -> None:
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

        # apply movement vector as force
        phys_actor.move.force.x = actor.state.delta.x

        # apply y-force is only applied if applicable
        if actor.state.delta.y != 0.0:
            applicable = False
            if is_on_ladder:
                applicable = True
            else:
                if phys_actor.move.force.y == 0.0 and actor.state.delta.y > 0.0:
                    applicable = True

            if applicable:
                phys_actor.move.force.y = actor.state.delta.y

        # avoid IDLE/HOLD blending over ATTACK/THROW
        if ani_action in [animations.Action.IDLE, animations.Action.HOLD] and \
           ani_actor.frame.action in [animations.Action.ATTACK, animations.Action.THROW]:
            return

        # attacking is priority over jumping/falling
        if ani_action in [animations.Action.JUMP, animations.Action.MOVE] and \
           ani_actor.frame.action in animations.BUSY_ANIMATIONS:
            return last_action

        # trigger resulting animation action
        ani_actor.frame.start(ani_action)

    def update(self, elapsed_ms: int) -> None:
        for actor in self.players_context.actors:
            actor.update(elapsed_ms, self.players_context.query)
            self.apply_input(actor)
