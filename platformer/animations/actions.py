from enum import IntEnum


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
BLOCKING_ANIMATIONS = [Action.DIE, Action.LANDING]

# animations that do not allow climbing
BUSY_ANIMATIONS = [Action.ATTACK, Action.THROW, Action.DIE]

# animations that are related to movement
MOVEMENT_ANIMATIONS = [Action.MOVE, Action.CLIMB]

# those loop until interrupted by user input
LOOPED_ANIMATIONS = [Action.IDLE, Action.MOVE, Action.HOLD]

# those animations lead to IDLE when finished
RESET_TO_IDLE_ANIMATIONS = [Action.ATTACK, Action.THROW, Action.LANDING]

# those animations freeze in the last frame
FREEZE_AT_END_ANIMATIONS = [Action.JUMP, Action.DIE]
