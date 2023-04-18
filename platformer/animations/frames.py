from dataclasses import dataclass

from core import constants
from . import actions

ANIMATION_FRAME_DURATION: int = 120


@dataclass
class FrameAnimation:
    """action is used as row index, frame_id as column index."""
    action: actions.Action = actions.Action.IDLE
    frame_id: int = 0
    duration_ms: int = ANIMATION_FRAME_DURATION
    max_duration_ms: int = ANIMATION_FRAME_DURATION

    def start(self, action: actions.Action, duration_ms: int = ANIMATION_FRAME_DURATION) -> bool:
        """Resets the frame animation with the given action.
        Returns True if the animation was actually started, False if the animation was started earlier.
        """
        if self.action == action:
            return False

        self.action = action
        self.frame_id = 0
        self.duration_ms = duration_ms
        self.max_duration_ms = duration_ms

        return True

    def step_frame(self, elapsed_ms) -> bool:
        """Continues the current animation and returns True if it was finished, else False."""
        self.duration_ms -= elapsed_ms

        while self.duration_ms <= 0:
            self.duration_ms += self.max_duration_ms
            self.frame_id += 1

        return self.frame_id >= constants.ANIMATION_NUM_FRAMES

    def handle_finish(self) -> None:
        """Handles animations to rewind, loop or freeze when finished."""
        if self.action in actions.LOOPED_ANIMATIONS:
            # loop
            self.frame_id = 0

        elif self.action in actions.RESET_TO_IDLE_ANIMATIONS:
            # reset to idle
            self.frame_id = 0
            self.action = actions.Action.IDLE

        elif self.action == actions.Action.CLIMB:
            # reset to hold
            self.frame_id = 0
            self.action = actions.Action.HOLD

        else:
            # freeze at last frame
            self.frame_id -= 1
