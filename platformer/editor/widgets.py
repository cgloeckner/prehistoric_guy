import imgui
import pygame
import math
from typing import List, Optional

from core import resources

from core import constants
from platformer import physics


MOUSE_SELECT_RADIUS: float = 0.2


def platform_ui(platform: physics.Platform) -> bool:
    with imgui.begin('Platform', closable=True) as handle:
        _, platform.pos.x = imgui.input_float('x', platform.pos.x, 0.1, 1.0, '%.1f')
        _, platform.pos.y = imgui.input_float('y', platform.pos.y, 0.1, 1.0, '%.1f')
        _, platform.width = imgui.slider_int('width', platform.width, 1, 20)
        _, platform.height = imgui.slider_int('height', platform.height, 0, 5)

        return not handle.opened


def ladder_ui(ladder: physics.Ladder) -> bool:
    with imgui.begin('Ladder', closable=True) as handle:
        _, ladder.pos.x = imgui.input_float('x', ladder.pos.x, 0.1, 1.0, '%.1f')
        _, ladder.pos.y = imgui.input_float('y', ladder.pos.y, 0.1, 1.0, '%.1f')
        _, ladder.height = imgui.slider_int('height', ladder.height, 0, 5)

        return not handle.opened


def object_ui(obj: physics.Object) -> bool:
    type_names = [value.name for value in constants.ObjectType]

    with imgui.begin('Object', closable=True) as handle:
        _, obj.pos.x = imgui.input_float('x', obj.pos.x, 0.1, 1.0, '%.1f')
        _, obj.pos.y = imgui.input_float('y', obj.pos.y, 0.1, 1.0, '%.1f')
        clicked, index = imgui.combo('object_type', obj.object_type, type_names)
        if clicked:
            obj.object_type = constants.ObjectType.__members__[type_names[index]]

        return not handle.opened


if __name__ == '__main__':
    from core.imgui_wrapper import OpenGlWrapper

    my_platform = physics.Platform(pos=pygame.math.Vector2(), width=1)
    my_ladder = physics.Ladder(pos=pygame.math.Vector2(), height=1)
    my_obj = physics.Object(pos=pygame.math.Vector2(), object_type=constants.ObjectType.FOOD)

    pygame.init()
    size = 800, 600

    screen = pygame.display.set_mode(size, OpenGlWrapper.get_display_flags())
    wrapper = OpenGlWrapper(screen)

    background = pygame.image.load('../../data/background.png')

    state = 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            wrapper.process_event(event)

        imgui.new_frame()

        if state == 0 and platform_ui(my_platform):
            state = 1
        if state == 1 and ladder_ui(my_ladder):
            state = 2
        if state == 2 and object_ui(my_obj):
            state = 0

        wrapper.buffer.fill('black')
        wrapper.buffer.blit(background, (0, 0))
        wrapper.render()

        pygame.display.flip()

"""



def get_dict_key_index(dictionary, value) -> int:
    index = 0
    for key in dictionary:
        if dictionary[key] == value:
            return index
        index += 1


def platform_ui(platform: physics.Platform) -> None:
    opts_dict = {
        'None': None,
        'sin': math.sin,
        'cos': math.cos
    }
    opts_keys = list(opts_dict.keys())

    with imgui.begin('Platform', True):
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


def actor_ui(phys_actor: physics.Actor, ani_actor: animations.Actor, render_actor: renderer.Actor) -> None:
    with imgui.begin('Actor', True):
        _, phys_actor.x = imgui.input_float('x', phys_actor.pos.x, 0.1)
        _, phys_actor.y = imgui.input_float('y', phys_actor.pos.y, 0.1)
        #imgui.text(f'face_x={phys_actor.face_x}')
        imgui.text(f'force_x={phys_actor.move.force.x}')
        imgui.text(f'force_y={phys_actor.move.force.y}')
        imgui.text(f'anchor={phys_actor.on_platform}')
        imgui.text(f'ladder={phys_actor.on_ladder}')
        _, phys_actor.radius = imgui.input_float('y', phys_actor.radius, 0.1)
        imgui.text(f'action_id={ani_actor.frame.action}')
        imgui.text(f'action_id={ani_actor.frame.action}')
        imgui.text(f'sprite_sheet={render_actor.sprite_sheet}')


def object_ui(obj: physics.Object) -> None:
    #opts_dict = {
    #    'FOOD_OBJ': FOOD_OBJ,
    #    'DANGER_OBJ': DANGER_OBJ,
    #    'BONUS_OBJ': BONUS_OBJ,
    #    'WEAPON_OBJ': WEAPON_OBJ
    #}
    #opts_keys = list(opts_dict.keys())

    with imgui.begin('Object', True):
        _, obj.x = imgui.input_float('x', obj.x, 0.1)
        _, obj.y = imgui.input_float('y', obj.y, 0.1)

        #clicked, current = imgui.combo('object_type', get_dict_key_index(opts_dict, obj.object_type), opts_keys)
        #if clicked:
        #    obj.object_type = opts_dict[opts_keys[current]]


def ladder_ui(ladder: physics.Ladder) -> None:
    with imgui.begin('Ladder', True):
        _, ladder.pos.x = imgui.input_float('x', ladder.pos.x, 0.1)
        _, ladder.pos.y = imgui.input_float('y', ladder.pos.y, 0.1)
        _, ladder.height = imgui.input_int('height', ladder.height, 1)

"""