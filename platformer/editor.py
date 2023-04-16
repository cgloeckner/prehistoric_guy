import imgui
import pygame
import math
from typing import List

from core import resources
from core import shapes

from platformer import physics
from platformer import animations
from platformer import render
from platformer import factory


MOUSE_SELECT_RADIUS: float = 0.2


def get_dict_key_index(dictionary, value) -> int:
    index = 0
    for key in dictionary:
        if dictionary[key] == value:
            return index
        index += 1


def platform_ui(platform: physics.Platform) -> bool:
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

    _, platform.pos.x = imgui.input_float('x', platform.pos.x, 0.1)
    _, platform.pos.y = imgui.input_float('y', platform.pos.y, 0.1)
    _, platform.width = imgui.input_int('width', platform.width, 0.1)
    _, platform.height = imgui.input_int('height', platform.height, 0.1)

    _, enabled = imgui.checkbox('does hover?', platform.hover is not None)
    if enabled and platform.hover is None:
        platform.hover = physics.Hovering()
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


def actor_ui(phys_actor: physics.Actor, ani_actor: animations.Actor, render_actor: render.Actor) -> bool:
    """Shows an ImGui-based UI for editing a given actor. Values are updated automatically.
    Returns True if the close button was clicked.
    """
    _, opened = imgui.begin('Actor', True)

    _, phys_actor.x = imgui.input_float('x', phys_actor.pos.x, 0.1)
    _, phys_actor.y = imgui.input_float('y', phys_actor.pos.y, 0.1)
    #imgui.text(f'face_x={phys_actor.face_x}')
    imgui.text(f'force_x={phys_actor.movement.force.x}')
    imgui.text(f'force_y={phys_actor.movement.force.y}')
    imgui.text(f'anchor={phys_actor.on_platform}')
    imgui.text(f'ladder={phys_actor.on_ladder}')
    _, phys_actor.radius = imgui.input_float('y', phys_actor.radius, 0.1)
    imgui.text(f'action_id={ani_actor.action}')
    imgui.text(f'action_id={ani_actor.action}')
    imgui.text(f'sprite_sheet={render_actor.sprite_sheet}')

    imgui.end()

    return not opened


def object_ui(obj: physics.Object) -> bool:
    """Shows an ImGui-based UI for editing a given object. Values are updated automatically.
    Returns True if the close button was clicked.
    """
    #opts_dict = {
    #    'FOOD_OBJ': FOOD_OBJ,
    #    'DANGER_OBJ': DANGER_OBJ,
    #    'BONUS_OBJ': BONUS_OBJ,
    #    'WEAPON_OBJ': WEAPON_OBJ
    #}
    #opts_keys = list(opts_dict.keys())

    _, opened = imgui.begin('Object', True)

    _, obj.x = imgui.input_float('x', obj.x, 0.1)
    _, obj.y = imgui.input_float('y', obj.y, 0.1)

    #clicked, current = imgui.combo('object_type', get_dict_key_index(opts_dict, obj.object_type), opts_keys)
    #if clicked:
    #    obj.object_type = opts_dict[opts_keys[current]]

    imgui.end()

    return not opened


def ladder_ui(ladder: physics.Ladder) -> bool:
    """Shows an ImGui-based UI for editing a given ladder. Values are updated automatically.
    Returns True if the close button was clicked.
    """
    _, opened = imgui.begin('Ladder', True)

    _, ladder.pos.x = imgui.input_float('x', ladder.pos.x, 0.1)
    _, ladder.pos.y = imgui.input_float('y', ladder.pos.y, 0.1)
    _, ladder.height = imgui.input_int('height', ladder.height, 1)

    imgui.end()

    return not opened


class SceneEditor(object):
    def __init__(self, screen: pygame.Surface, obj_manager: factory.ObjectManager):
        self.screen = screen
        self.obj_manager = obj_manager

        self.hovered_elements = list()
        self.selected = None

    def get_mouse_world_pos(self) -> pygame.math.Vector2:
        # transform screen coordinates to game coordinates
        return self.obj_manager.camera.screen_to_world_coord(*pygame.mouse.get_pos())

    def get_hovered(self) -> List:
        pos = self.get_mouse_world_pos()
        circ1 = shapes.Circ(*pos, MOUSE_SELECT_RADIUS)

        # collect all hoverable objects
        hovered = list()
        for platform in self.obj_manager.context.platforms:
            line = platform.get_line()
            if platform.contains_point(pos) or circ1.collideline(line):
                hovered.append(platform)

        for actor in self.obj_manager.context.actors:
            circ2 = actor.get_circ()
            if circ1.collidecirc(circ2):
                hovered.append(actor)

        for obj in self.obj_manager.context.objects:
            circ2 = obj.get_circ()
            if circ1.collidecirc(circ2):
                hovered.append(obj)

        for ladder in self.obj_manager.context.ladders:
            if ladder.is_in_reach_of(pos):
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
            elem.hsl = resources.HslTransform(hue=50, saturation=100)

        # select first hovered element on click
        left_click = pygame.mouse.get_pressed()[0]
        if left_click and self.selected is None and len(self.hovered_elements) > 0:
            self.selected = self.hovered_elements[0]

    def update(self) -> None:
        self.update_hover()

    def draw(self) -> None:
        if isinstance(self.selected, physics.Platform) and platform_ui(self.selected):
            self.selected = None

        if isinstance(self.selected, physics.Actor):
            ani_actor = self.obj_manager.animation.get_by_id(self.selected.object_id)
            render_actor = self.obj_manager.renderer.get_by_id(self.selected.object_id)
            if actor_ui(self.selected, ani_actor, render_actor):
                self.selected = None

        if isinstance(self.selected, physics.Object) and object_ui(self.selected):
            self.selected = None

        if isinstance(self.selected, physics.Ladder) and ladder_ui(self.selected):
            self.selected = None
