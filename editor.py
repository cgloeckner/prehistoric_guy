import imgui
import pygame
import math
from typing import List

import platformer


def get_dict_key_index(dictionary, value) -> int:
    index = 0
    for key in dictionary:
        if dictionary[key] == value:
            return index
        index += 1


def platform_ui(platform: platformer.Platform) -> bool:
    """Shows an ImGui-based UI for editing the given platform. Values are updated automatically.
    Returns True if the close button was clicked.
    """
    opts_dict = {
        'None': None,
        'sin': math.sin,
        'cos': math.cos
    }
    opts_keys = list(opts_dict.keys())

    _, opened = imgui.begin('Platform', True)

    _, platform.x = imgui.input_float('x', platform.x, 0.1)
    _, platform.y = imgui.input_float('y', platform.y, 0.1)
    _, platform.width = imgui.input_float('width', platform.width, 0.1)
    _, platform.height = imgui.input_float('height', platform.height, 0.1)

    _, enabled = imgui.checkbox('does hover?', platform.hover is not None)
    if enabled and platform.hover is None:
        platform.hover = platformer.Hovering()
    if not enabled and platform.hover is not None:
        platform.hover = None

    if platform.hover is not None:
        clicked, current = imgui.combo('hover.x', get_dict_key_index(opts_dict, platform.hover.x), opts_keys)
        if clicked:
            platform.hover.x = opts_dict[opts_keys[current]]

        clicked, current = imgui.combo('hover.y', get_dict_key_index(opts_dict, platform.hover.y), opts_keys)
        if clicked:
            platform.hover.y = opts_dict[opts_keys[current]]

        _, platform.hover.amplitude = imgui.input_float('amplitude', platform.hover.amplitude, 0.1)

    imgui.end()

    return not opened


def sprite_ui(sprite: platformer.Actor) -> bool:
    """Shows an ImGui-based UI for editing a given actor. Values are updated automatically.
    Returns True if the close button was clicked.
    """
    _, opened = imgui.begin('Sprite', True)

    _, sprite.actor.x = imgui.input_float('x', sprite.actor.x, 0.1)
    _, sprite.actor.y = imgui.input_float('y', sprite.actor.y, 0.1)
    imgui.text(f'face_x={sprite.actor.face_x}')
    imgui.text(f'force_x={sprite.actor.force_x}')
    imgui.text(f'force_y={sprite.actor.force_y}')
    imgui.text(f'fall_from_y={sprite.actor.fall_from_y}')
    imgui.text(f'anchor={sprite.actor.anchor}')
    imgui.text(f'ladder={sprite.actor.ladder}')
    _, sprite.actor.radius = imgui.input_float('y', sprite.actor.radius, 0.1)
    imgui.text(f'action_id={sprite.animation.action_id}')

    imgui.end()

    return not opened


def object_ui(obj: platformer.Object) -> bool:
    """Shows an ImGui-based UI for editing a given object. Values are updated automatically.
    Returns True if the close button was clicked.
    """
    opts_dict = {
        'FOOD_OBJ': platformer.FOOD_OBJ,
        'DANGER_OBJ': platformer.DANGER_OBJ,
        'BONUS_OBJ': platformer.BONUS_OBJ,
        'WEAPON_OBJ': platformer.WEAPON_OBJ
    }
    opts_keys = list(opts_dict.keys())

    _, opened = imgui.begin('Object', True)

    _, obj.x = imgui.input_float('x', obj.x, 0.1)
    _, obj.y = imgui.input_float('y', obj.y, 0.1)

    clicked, current = imgui.combo('object_type', get_dict_key_index(opts_dict, obj.object_type), opts_keys)
    if clicked:
        obj.object_type = opts_dict[opts_keys[current]]

    imgui.end()

    return not opened


def ladder_ui(ladder: platformer.Ladder) -> bool:
    """Shows an ImGui-based UI for editing a given ladder. Values are updated automatically.
    Returns True if the close button was clicked.
    """
    _, opened = imgui.begin('Ladder', True)

    _, ladder.x = imgui.input_float('x', ladder.x, 0.1)
    _, ladder.y = imgui.input_float('y', ladder.y, 0.1)
    _, ladder.height = imgui.input_int('height', ladder.height, 1)

    imgui.end()

    return not opened


class SceneEditor(object):
    def __init__(self, screen: pygame.Surface, obj_manager: platformer.ObjectManager):
        self.screen = screen
        self.obj_manager = obj_manager

        self.hovered_elements = list()
        self.selected = None

    def get_mouse_world_pos(self) -> pygame.math.Vector2:
        # transform screen coordinates to game coordinates
        return self.obj_manager.renderer.screen_to_world_coord(*pygame.mouse.get_pos())

    def get_hovered(self) -> List:
        pos = self.get_mouse_world_pos()

        # collect all hoverable objects
        hovered = list()
        for platform in self.obj_manager.physics.platforms:
            h = platform.height if platform.height > 0.0 else platformer.OBJECT_RADIUS
            if platform.x <= pos.x <= platform.x + platform.width and platform.y - h <= pos.y <= platform.y:
                hovered.append(platform)

        for actor in self.obj_manager.physics.actors:
            actor_pos = pygame.math.Vector2(actor.x, actor.y + actor.radius)
            distance = pos.distance_squared_to(actor_pos)
            if distance <= actor.radius ** 2:
                hovered.append(actor)

        for obj in self.obj_manager.physics.objects:
            obj_pos = pygame.math.Vector2(obj.x, obj.y + platformer.OBJECT_RADIUS)
            distance = pos.distance_squared_to(obj_pos)
            if distance <= platformer.OBJECT_RADIUS ** 2:
                hovered.append(obj)

        for ladder in self.obj_manager.physics.ladders:
            if platformer.ladder_in_reach(pos.x, pos.y, ladder):
                hovered.append(ladder)

        return hovered

    def update_hover(self) -> None:
        if self.selected is not None:
            # do not alter element hovering (coloring)
            return

        # update coloring for hovered elements
        for elem in self.hovered_elements:
            elem.hsl = None
        self.hovered_elements = self.get_hovered()
        for elem in self.hovered_elements:
            elem.hsl = platformer.HslTransform(hue=0.14, saturation=1.0)

        # select first hovered element on click
        left_click = pygame.mouse.get_pressed()[0]
        if left_click and self.selected is None and len(self.hovered_elements) > 0:
            self.selected = self.hovered_elements[0]

    def update(self) -> None:
        self.update_hover()

    def draw(self) -> None:
        if isinstance(self.selected, platformer.Platform) and platform_ui(self.selected):
            self.selected = None

        if isinstance(self.selected, platformer.Actor):
            sprite = [sprite for sprite in self.obj_manager.renderer.sprites if sprite.actor == self.selected][0]
            if sprite_ui(sprite):
                self.selected = None

        if isinstance(self.selected, platformer.Object) and object_ui(self.selected):
            self.selected = None

        if isinstance(self.selected, platformer.Ladder) and ladder_ui(self.selected):
            self.selected = None
