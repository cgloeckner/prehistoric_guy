import math
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional, List
from enum import IntEnum

from core.constants import *
from core import resources


ANIMATION_FRAME_DURATION: int = 120

MOVEMENT_SWING: float = 1.0
CLIMB_SWING: float = 7.0


class Action(IntEnum):
    IDLE = 0
    MOVE = 1
    HOLD = 2
    CLIMB = 3
    ATTACK = 4
    THROW = 5
    JUMP = 6
    LANDING = 7
    DIE = 8


# animations that cannot be interrupted by user input
BLOCKING_ANIMATIONS = [Action.DIE, Action.ATTACK, Action.THROW, Action.LANDING]

# those loop until interrupted by user input
LOOPED_ANIMATIONS = [Action.IDLE, Action.MOVE, Action.HOLD]

# those animations lead to IDLE when finished
RESET_TO_IDLE_ANIMATIONS = [Action.ATTACK, Action.THROW, Action.LANDING]

# those animations freeze in the last frame
FREEZE_AT_END_ANIMATIONS = [Action.JUMP, Action.DIE]


@dataclass
class Actor:
    object_id: int

    # frame animation: row and column index, animation delay until frame is switched
    action: Action = Action.IDLE
    frame_id: int = 0
    frame_duration_ms: int = ANIMATION_FRAME_DURATION
    frame_max_duration_ms: int = ANIMATION_FRAME_DURATION
    # movement animation
    delta_y: float = 0.0
    total_frame_time_ms: int = 0
    # hsl animation
    hsl: Optional[resources.HslTransform] = None
    hsl_duration_ms: int = ANIMATION_FRAME_DURATION


def start(ani: Actor, action: Action, duration_ms: int = ANIMATION_FRAME_DURATION) -> None:
    """Resets the frame animation with the given action.
    """
    if ani.action == action:
        return

    ani.action = action
    ani.frame_id = 0
    ani.frame_duration_ms = duration_ms
    ani.frame_max_duration_ms = duration_ms
    ani.total_frame_time_ms = 0


def flash(ani: Actor, hsl: resources.HslTransform, duration_ms: int = ANIMATION_FRAME_DURATION) -> None:
    """Resets the color animation with the given color.
    """
    ani.hsl = hsl
    ani.hsl_duration_ms = duration_ms


class EventListener(ABC):

    @abstractmethod
    def on_step(self, ani: Actor) -> None:
        """Triggered when a cycle of a move animation finished.
        """
        pass

    @abstractmethod
    def on_climb(self, ani: Actor) -> None:
        """Triggered when a cycle of a climbing animation finished.
        """
        pass

    @abstractmethod
    def on_attack(self, ani: Actor) -> None:
        """Triggered when an attack animation finished.
        """
        pass

    @abstractmethod
    def on_throw(self, ani: Actor) -> None:
        """Triggered when a throwing animation finished.
        """
        pass

    @abstractmethod
    def on_died(self, ani: Actor) -> None:
        """Triggered when a dying animation finished.
        """
        pass


class Animating(object):
    """Handles all frame set animations.
    """
    def __init__(self, animation_listener: EventListener):
        self.animations: List[Actor] = list()
        self.event_listener = animation_listener

    def get_by_id(self, object_id: int) -> Actor:
        """Returns the animation who matches the given object_id.
        May throw an IndexError.
        """
        return [a for a in self.animations if a.object_id == object_id][0]

    def notify_animation(self, ani: Actor) -> None:
        """Notify about a finished animation.
        """
        if ani.action == Action.MOVE:
            self.event_listener.on_step(ani)
        elif ani.action == Action.ATTACK:
            self.event_listener.on_attack(ani)
        elif ani.action == Action.THROW:
            self.event_listener.on_throw(ani)
        elif ani.action == Action.DIE:
            self.event_listener.on_died(ani)

    def update_frame(self, ani: Actor, elapsed_ms: int) -> None:
        """Update a single frame animation.
        """
        # continue animation
        ani.frame_duration_ms -= elapsed_ms
        if ani.frame_duration_ms > 0:
            return

        while ani.frame_duration_ms < 0:
            ani.frame_duration_ms += ani.frame_max_duration_ms
            ani.frame_id += 1

        if ani.frame_id < ANIMATION_NUM_FRAMES:
            return

        # handle animation type (loop, reset, freeze)
        self.notify_animation(ani)

        if ani.action in LOOPED_ANIMATIONS:
            # loop
            ani.frame_id = 0
        elif ani.action in RESET_TO_IDLE_ANIMATIONS:
            # reset to idle
            ani.frame_id = 0
            ani.action = Action.IDLE
        elif ani.action == Action.CLIMB:
            # reset to hold
            ani.frame_id = 0
            ani.action = Action.HOLD
        else:
            # freeze at last frame
            ani.frame_id -= 1

    def update_hsl(self, ani: Actor, elapsed_ms: int) -> None:
        if ani.hsl is None:
            return

        ani.hsl_duration_ms -= elapsed_ms
        if ani.hsl_duration_ms > 0:
            return

        ani.hsl_duration_ms = 0
        ani.hsl = None

    def update_movement(self, ani: Actor, elapsed_ms: int) -> None:
        """Updates the movement animation, where a small height difference is applied while moving and climbing.
        """
        if ani.action not in [Action.MOVE, Action.CLIMB]:
            ani.total_frame_time_ms = 0
            return

        ani.total_frame_time_ms += elapsed_ms
        if ani.action == Action.MOVE:
            # |sin(x)|
            angle = 2 * math.pi * ani.total_frame_time_ms / 360
            ani.delta_y = MOVEMENT_SWING * math.sin(angle / MOVEMENT_SWING)
        else:
            # sawtooth
            value = ani.total_frame_time_ms / 1000.0
            ani.delta_y = CLIMB_SWING * (value - int(value))

    def update(self, elapsed_ms: int) -> None:
        """Updates all animations' frame durations. It automatically switches frames and loops/returns/freezes the
        animation once finished.
        """
        for ani in self.animations:
            self.update_frame(ani, elapsed_ms)
            self.update_hsl(ani, elapsed_ms)
            self.update_movement(ani, elapsed_ms)
