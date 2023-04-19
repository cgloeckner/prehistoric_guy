import imgui
import pygame

from core import constants
from platformer import physics


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
