"""
Based on
- imgui's pygame-integration example
    URL: https://github.com/pyimgui/pyimgui/blob/master/doc/examples/integrations_pygame.py
- PygameRenderer's bugfix from pyimgui/dev/version-2.0:
    URL: https://github.com/pyimgui/pyimgui/blob/dev/version-2.0/imgui/integrations/pygame.py
- "How can I blit [...] onto an OpenGL surface"
    URL: https://stackoverflow.com/questions/61396799/how-can-i-blit-my-pygame-game-onto-an-opengl-surface
"""

from imgui.integrations.opengl import FixedPipelineRenderer

import pygame
import pygame.event
import pygame.time

import imgui

import sys

import pygame
import OpenGL.GL as gl



class PygameRenderer(FixedPipelineRenderer):
    def __init__(self):
        super(PygameRenderer, self).__init__()

        self._gui_time = None
        self.custom_key_map = {}

        self._map_keys()

    def _custom_key(self, key):
        # We need to go to custom keycode since imgui only support keycod from 0..512 or -1
        if not key in self.custom_key_map:
            self.custom_key_map[key] = len(self.custom_key_map)
        return self.custom_key_map[key]

    def _map_keys(self):
        key_map = self.io.key_map

        key_map[imgui.KEY_TAB] = self._custom_key(pygame.K_TAB)
        key_map[imgui.KEY_LEFT_ARROW] = self._custom_key(pygame.K_LEFT)
        key_map[imgui.KEY_RIGHT_ARROW] = self._custom_key(pygame.K_RIGHT)
        key_map[imgui.KEY_UP_ARROW] = self._custom_key(pygame.K_UP)
        key_map[imgui.KEY_DOWN_ARROW] = self._custom_key(pygame.K_DOWN)
        key_map[imgui.KEY_PAGE_UP] = self._custom_key(pygame.K_PAGEUP)
        key_map[imgui.KEY_PAGE_DOWN] = self._custom_key(pygame.K_PAGEDOWN)
        key_map[imgui.KEY_HOME] = self._custom_key(pygame.K_HOME)
        key_map[imgui.KEY_END] = self._custom_key(pygame.K_END)
        key_map[imgui.KEY_INSERT] = self._custom_key(pygame.K_INSERT)
        key_map[imgui.KEY_DELETE] = self._custom_key(pygame.K_DELETE)
        key_map[imgui.KEY_BACKSPACE] = self._custom_key(pygame.K_BACKSPACE)
        key_map[imgui.KEY_SPACE] = self._custom_key(pygame.K_SPACE)
        key_map[imgui.KEY_ENTER] = self._custom_key(pygame.K_RETURN)
        key_map[imgui.KEY_ESCAPE] = self._custom_key(pygame.K_ESCAPE)
        # key_map[imgui.KEY_PAD_ENTER] = self._custom_key(pygame.K_KP_ENTER)
        key_map[imgui.KEY_A] = self._custom_key(pygame.K_a)
        key_map[imgui.KEY_C] = self._custom_key(pygame.K_c)
        key_map[imgui.KEY_V] = self._custom_key(pygame.K_v)
        key_map[imgui.KEY_X] = self._custom_key(pygame.K_x)
        key_map[imgui.KEY_Y] = self._custom_key(pygame.K_y)
        key_map[imgui.KEY_Z] = self._custom_key(pygame.K_z)

    def process_event(self, event):
        # perf: local for faster access
        io = self.io

        if event.type == pygame.MOUSEMOTION:
            io.mouse_pos = event.pos
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                io.mouse_down[0] = 1
            if event.button == 2:
                io.mouse_down[1] = 1
            if event.button == 3:
                io.mouse_down[2] = 1
            return True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                io.mouse_down[0] = 0
            if event.button == 2:
                io.mouse_down[1] = 0
            if event.button == 3:
                io.mouse_down[2] = 0
            if event.button == 4:
                io.mouse_wheel = .5
            if event.button == 5:
                io.mouse_wheel = -.5
            return True

        if event.type == pygame.KEYDOWN:
            for char in event.unicode:
                code = ord(char)
                if 0 < code < 0x10000:
                    io.add_input_character(code)

            io.keys_down[self._custom_key(event.key)] = True

        if event.type == pygame.KEYUP:
            io.keys_down[self._custom_key(event.key)] = False

        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            io.key_ctrl = (
                    io.keys_down[self._custom_key(pygame.K_LCTRL)] or
                    io.keys_down[self._custom_key(pygame.K_RCTRL)]
            )

            io.key_alt = (
                    io.keys_down[self._custom_key(pygame.K_LALT)] or
                    io.keys_down[self._custom_key(pygame.K_RALT)]
            )

            io.key_shift = (
                    io.keys_down[self._custom_key(pygame.K_LSHIFT)] or
                    io.keys_down[self._custom_key(pygame.K_RSHIFT)]
            )

            io.key_super = (
                    io.keys_down[self._custom_key(pygame.K_LSUPER)] or
                    io.keys_down[self._custom_key(pygame.K_LSUPER)]
            )

            return True

        if event.type == pygame.VIDEORESIZE:
            surface = pygame.display.get_surface()
            # note: pygame does not modify existing surface upon resize,
            #       we need to to it ourselves.
            pygame.display.set_mode(
                (event.w, event.h),
                flags=surface.get_flags(),
            )
            # existing font texure is no longer valid, so we need to refresh it
            self.refresh_font_texture()

            # notify imgui about new window size
            io.display_size = event.size

            # delete old surface, it is no longer needed
            del surface

            return True

    def process_inputs(self):
        io = imgui.get_io()

        current_time = pygame.time.get_ticks() / 1000.0

        if self._gui_time:
            io.delta_time = current_time - self._gui_time
        else:
            io.delta_time = 1. / 60.
        if (io.delta_time <= 0.0): io.delta_time = 1. / 1000.
        self._gui_time = current_time


import OpenGL.GL as gl

texID = 0


def init(size):
    # basic opengl configuration
    gl.glViewport(0, 0, *size)
    gl.glDepthRange(0, 1)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    gl.glShadeModel(gl.GL_SMOOTH)
    gl.glClearColor(0.0, 0.0, 0.0, 0.0)
    gl.glClearDepth(1.0)
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_LIGHTING)
    gl.glDepthFunc(gl.GL_LEQUAL)
    gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)
    gl.glEnable(gl.GL_BLEND)

    texID = gl.glGenTextures(1)


def surfaceToTexture(texID, pygame_surface):
    rgb_surface = pygame.image.tostring(pygame_surface, 'RGB')
    gl.glBindTexture(gl.GL_TEXTURE_2D, texID)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
    surface_rect = pygame_surface.get_rect()
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, surface_rect.width, surface_rect.height, 0, gl.GL_RGB,
                    gl.GL_UNSIGNED_BYTE, rgb_surface)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


def main():
    pygame.init()
    size = 800, 600

    screen = pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
    init(size)

    buffer = pygame.Surface(size)

    imgui.create_context()
    impl = PygameRenderer()

    io = imgui.get_io()
    io.display_size = size
    
    background = pygame.image.load('data/background.png')

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            impl.process_event(event)

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        imgui.show_test_window()

        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_colored("Eggs", 0.2, 1., 0.)
        imgui.end()

        buffer.fill('black')
        buffer.blit(background, (0, 0))

        # prepare to render the texture-mapped rectangle
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glDisable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_TEXTURE_2D)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glClearColor(0, 0, 0, 1.0)

        # draw texture openGL Texture
        surfaceToTexture(texID, buffer)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texID)
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0, 0);
        gl.glVertex2f(-1, 1)
        gl.glTexCoord2f(0, 1);
        gl.glVertex2f(-1, -1)
        gl.glTexCoord2f(1, 1);
        gl.glVertex2f(1, -1)
        gl.glTexCoord2f(1, 0);
        gl.glVertex2f(1, 1)
        gl.glEnd()

        # note: cannot use screen.fill((1, 1, 1)) because pygame's screen
        #       does not support fill() on OpenGL sufraces
        # gl.glClearColor(1, 1, 1, 1)
        # gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())

        screen.blit(buffer, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main()
