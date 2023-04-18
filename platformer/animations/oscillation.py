import math
from dataclasses import dataclass

from . import actions

MOVEMENT_SWING: float = 1.0
CLIMB_SWING: float = 7.0


@dataclass
class OscillateAnimation:
    delta_y: float = 0.0
    total_time_ms: int = 0

    def get_move_swing(self) -> float:
        """Returns delta-y for oscillated movement animation using sin."""
        angle = 2 * math.pi * self.total_time_ms / 360
        return MOVEMENT_SWING * math.sin(angle / MOVEMENT_SWING)

    def get_climb_swing(self) -> float:
        """Returns delta-y for oscillated climbing animation using a sawtooth."""
        value = self.total_time_ms / 1000.0
        return CLIMB_SWING * (value - int(value))

    def update(self, action: actions.Action, elapsed_ms: int) -> None:
        """Applies the delta-y for an oscillated animation, based on the animation type."""
        if action not in [actions.Action.MOVE, actions.Action.CLIMB]:
            self.total_time_ms = 0
            return

        self.total_time_ms += elapsed_ms

        if action == actions.Action.MOVE:
            self.delta_y = self.get_move_swing()

        elif action == actions.Action.CLIMB:
            self.delta_y = self.get_climb_swing()
