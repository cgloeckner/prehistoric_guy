import imgui
import pygame
import math
from typing import List, Optional

from constants import WORLD_SCALE
import platforms
import factory


def get_dict_key_index(dictionary, value) -> int:
    index = 0
    for key in dictionary:
        if dictionary[key] == value:
            return index
        index += 1


def platform_ui(platform: platforms.Platform) -> bool:
    """Shows an ImGui-based UI for editing the given platform. Values are changed automatically.
    Returns True if the close button was clicked.
    """
    float_opts = {
        'None': None,
        'sin': math.sin,
        'cos': math.cos
    }
    opts_keys = list(float_opts.keys())

    _, opened = imgui.begin('Platform', True)

    _, platform.x = imgui.input_float('x', platform.x, 0.1)
    _, platform.y = imgui.input_float('y', platform.y, 0.1)
    _, platform.width = imgui.input_float('width', platform.width, 0.1)
    _, platform.height = imgui.input_float('height', platform.height, 0.1)

    _, enabled = imgui.checkbox('does hover?', platform.hover is not None)
    if enabled and platform.hover is None:
        platform.hover = platforms.Hovering()
    if not enabled and platform.hover is not None:
        platform.hover = None

    if platform.hover is not None:
        clicked, current = imgui.combo('hover.x', get_dict_key_index(float_opts, platform.hover.x), opts_keys)
        if clicked:
            platform.hover.x = float_opts[opts_keys[current]]

        clicked, current = imgui.combo('hover.y', get_dict_key_index(float_opts, platform.hover.y), opts_keys)
        if clicked:
            platform.hover.y = float_opts[opts_keys[current]]

        _, platform.hover.amplitude = imgui.input_float('amplitude', platform.hover.amplitude, 0.1)

    imgui.end()

    return not opened


class SceneEditor(object):
    def __init__(self, screen: pygame.Surface, obj_manager: factory.ObjectManager):
        self.screen = screen
        self.obj_manager = obj_manager

        self.hovered_elements = list()
        self.selected = None

    def get_hovered(self, screen: pygame.Surface) -> List:
        # transform screen coordinates to game coordinates (keep in mind that the screen was upscaled by x2)
        x, y = pygame.mouse.get_pos()
        y = screen.get_height() - y
        x //= 2
        y //= 2
        x /= WORLD_SCALE
        y /= WORLD_SCALE
        pos = pygame.math.Vector2(x, y)

        # collect all hoverable objects
        hovered = list()
        for platform in self.obj_manager.physics.platforms:
            h = platform.height if platform.height > 0.0 else platforms.OBJECT_RADIUS
            if platform.x <= x <= platform.x + platform.width and platform.y - h <= y <= platform.y:
                hovered.append(platform)

        for actor in self.obj_manager.physics.actors:
            actor_pos = pygame.math.Vector2(actor.pos_x, actor.pos_y + actor.radius)
            distance = pos.distance_squared_to(actor_pos)
            if distance <= actor.radius ** 2:
                hovered.append(actor)

        for obj in self.obj_manager.physics.objects:
            obj_pos = pygame.math.Vector2(obj.pos_x, obj.pos_y + platforms.OBJECT_RADIUS)
            distance = pos.distance_squared_to(obj_pos)
            if distance <= platforms.OBJECT_RADIUS ** 2:
                hovered.append(obj)

        return hovered

    def update(self) -> None:
        if self.selected is not None:
            # do not alter element coloring
            return

        # update coloring for hovered elements
        for elem in self.hovered_elements:
            elem.color = None
        self.hovered_elements = self.get_hovered(self.screen)
        for elem in self.hovered_elements:
            elem.color = pygame.Color(255, 255, 255)

        # select first hovered element on click
        left_click = pygame.mouse.get_pressed()[0]
        if left_click and self.selected is None and len(self.hovered_elements) > 0:
            self.selected = self.hovered_elements[0]
            print(self.selected)

    def draw(self) -> None:
        if isinstance(self.selected, platforms.Platform):
            if platform_ui(self.selected):
                self.selected = None
