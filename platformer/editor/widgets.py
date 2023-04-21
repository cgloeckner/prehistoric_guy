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


def hover_editor(hover: physics.Hovering, hover_label: str, amplitude_label: str) -> bool:
    """Provides editor UI for hovering information and returns whether it was changed.
    """
    type_list = [value for value in physics.HoverType.__members__]

    changed_x, index_x = imgui.combo(f'{hover_label} x', hover.x, type_list)
    if changed_x:
        hover.x = physics.HoverType(index_x)

    changed_y, index_y = imgui.combo(f'{hover_label} y', hover.y, type_list)
    if changed_y:
        hover.y = physics.HoverType(index_y)

    changed_amplitude, hover.amplitude = imgui.input_float(f'{amplitude_label} x', hover.amplitude, 0.1, 1.0)

    return changed_x or changed_y or changed_amplitude


def platform_editor(platform: physics.Platform, pos_label: str, width_label: str, height_label: str,
                    type_label: str, amplitude_label: str) -> bool:
    """Provides editor UI for a platform and returns whether it was changed."""
    if not hasattr(platform, 'original_pos'):
        # initialize copy position
        platform.original_pos = platform.pos.copy()

    changed_pos = position_editor(platform.original_pos, pos_label)
    if changed_pos:
        # update position
        platform.pos = platform.original_pos.copy() + platform.hover.delta

    changed_w, value = imgui.input_int(width_label, platform.width, 1)
    if changed_w:
        if value <= 0:
            value = 1
        platform.width = value

    changed_h, value = imgui.input_int(height_label, platform.height, 1)
    if changed_h:
        if value < 0:
            value = 0
        platform.height = value

    changed_hover = hover_editor(platform.hover, type_label, amplitude_label)
    if changed_hover:
        # reset hovering
        platform.pos = platform.original_pos + platform.hover.delta
        platform.hover.index = 0

    return changed_pos or changed_w or changed_h or changed_hover


def ladder_editor(ladder: physics.Ladder, pos_label: str, height_label: str) -> bool:
    """Provides editor UI for a ladder and returns whether it was changed."""
    changed_pos = position_editor(ladder.pos, pos_label)

    changed_h, value = imgui.input_int(height_label, ladder.height, 1)
    if changed_h:
        if value <= 0:
            value = 1
        ladder.height = value

    return changed_pos or changed_h


def object_editor(obj: physics.Object, pos_label: str, type_label: str) -> bool:
    """Provides editor UI for an object and returns whether it was changed."""
    changed_pos = position_editor(obj.pos, pos_label)

    type_list = [value for value in constants.ObjectType.__members__]
    changed_t, index = imgui.combo(type_label, obj.object_type, type_list)
    if changed_t:
        obj.object_type = constants.ObjectType(index)

    return changed_pos or changed_t
