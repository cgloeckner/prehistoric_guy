from enum import IntEnum

WORLD_SCALE: int = 32
OBJECT_SCALE: int = WORLD_SCALE // 2
SPRITE_SCALE: int = WORLD_SCALE * 2

ANIMATION_NUM_FRAMES: int = 4

NUM_SCALE_DOUBLE: int = 0

RESOLUTION_X: int = WORLD_SCALE * 10 * 2 ** NUM_SCALE_DOUBLE
RESOLUTION_Y: int = int(RESOLUTION_X * 0.625)  # 320x200 aspect ratio

SPRITE_CLOTHES_COLORS = ['#ff0000', '#800000', '#bf0000']


class ObjectType(IntEnum):
    FOOD = 0
    DANGER = 1
    BONUS = 2
    WEAPON = 3


OBJECT_RADIUS: float = 0.25

OBJECT_NUM_VERSIONS: int = 6
