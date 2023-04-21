import pygame
import imgui

from core import constants
from platformer import physics


def position_editor(pos: pygame.math.Vector2, label: str) -> bool:
    """Provides editor UI for a position vector and returns whether it was changed.
    """
    changed_x, pos.x = imgui.input_float(f'{label} x', pos.x, 0.1, 1.0)
    changed_y, pos.y = imgui.input_float(f'{label} y', pos.y, 0.1, 1.0)
    return changed_x or changed_y


def platform_editor(platform: physics.Platform, pos_label: str, width_label: str, height_label: str) -> bool:
    """Provides editor UI for a platform and returns whether it was changed."""
    has_changed = position_editor(platform.pos, pos_label)

    changed, value = imgui.input_int(width_label, platform.width, 1)
    if changed:
        if value <= 0:
            value = 1
        platform.width = value
        has_changed = True

    changed, value = imgui.input_int(height_label, platform.height, 1)
    if changed:
        if value < 0:
            value = 0
        platform.height = value
        has_changed = True

    return has_changed


def ladder_editor(ladder: physics.Ladder, pos_label: str, height_label: str) -> bool:
    """Provides editor UI for a ladder and returns whether it was changed."""
    has_changed = position_editor(ladder.pos, pos_label)

    changed, value = imgui.input_int(height_label, ladder.height, 1)
    if changed:
        if value <= 0:
            value = 1
        ladder.height = value
        has_changed = True

    return has_changed


def object_editor(obj: physics.Object, pos_label: str, type_label: str) -> bool:
    """Provides editor UI for an object and returns whether it was changed."""
    has_changed = position_editor(obj.pos, pos_label)

    type_list = [value for value in constants.ObjectType.__members__]
    clicked, index = imgui.combo(type_label, obj.object_type, type_list)
    if clicked:
        obj.object_type = constants.ObjectType(index)
        has_changed = True

    return has_changed
