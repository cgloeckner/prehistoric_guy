from enum import IntEnum

DOES_SCALE_2X: bool = True

WORLD_SCALE: int = 32 * 2 ** DOES_SCALE_2X
OBJECT_SCALE: int = WORLD_SCALE // 2
SPRITE_SCALE: int = WORLD_SCALE * 2

ANIMATION_NUM_FRAMES: int = 4

RESOLUTION_X: int = WORLD_SCALE * 20
RESOLUTION_Y: int = int(RESOLUTION_X * 0.625)  # 640x400 aspect ratio

SPRITE_CLOTHES_COLORS = ['#42200f', '#834222', '#9d633d']
SNOW_CLOTHES_COLORS = ['#8996c6', '#aac2ff', '#a5acc4']
GRASS_CLOTHES_COLOR = ['#0c2618', '#123924', '#266e48']
STONE_CLOTHES_COLOR = ['#4a4a4a', '#8c8c8c', '#adadad']
EMBER_CLOTHES_COLOR = ['#ad0021', '#ef6221', '#efce21']


class ObjectType(IntEnum):
    FOOD = 0
    DANGER = 1
    BONUS = 2
    WEAPON = 3


OBJECT_RADIUS: float = 0.25

OBJECT_NUM_VERSIONS: int = 6
