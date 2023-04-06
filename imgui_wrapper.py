"""
Based on
- imgui's pygame-integration example
    URL: https://github.com/pyimgui/pyimgui/blob/master/doc/examples/integrations_pygame.py
- PygameRenderer's bugfix from pyimgui/dev/version-2.0:
    URL: https://github.com/pyimgui/pyimgui/blob/dev/version-2.0/imgui/integrations/pygame.py
- "How can I blit [...] onto an OpenGL surface"
    URL: https://stackoverflow.com/questions/61396799/how-can-i-blit-my-pygame-game-onto-an-opengl-surface
"""

import pygame

import imgui
from imgui.integrations.opengl import FixedPipelineRenderer

import OpenGL.GL


class PygameRenderer(FixedPipelineRenderer):
    """Custom Renderer implementation that fixes a keycode issue with imgui v1.4.1
    This may become obsolete once imgui v2.0 is finished.
    """
    def __init__(self):
        super(PygameRenderer, self).__init__()

        self._gui_time = None
        self.custom_key_map = {}

        self._map_keys()

    def _custom_key(self, key):
        # We need to go to custom keycode since imgui only support keycode from 0..512 or -1
        if key not in self.custom_key_map:
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

    def process_event(self, ev):
        # perf: local for faster access
        io = self.io

        if ev.type == pygame.MOUSEMOTION:
            io.mouse_pos = ev.pos
            return True

        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 1:
                io.mouse_down[0] = 1
            if ev.button == 2:
                io.mouse_down[1] = 1
            if ev.button == 3:
                io.mouse_down[2] = 1
            return True

        if ev.type == pygame.MOUSEBUTTONUP:
            if ev.button == 1:
                io.mouse_down[0] = 0
            if ev.button == 2:
                io.mouse_down[1] = 0
            if ev.button == 3:
                io.mouse_down[2] = 0
            if ev.button == 4:
                io.mouse_wheel = .5
            if ev.button == 5:
                io.mouse_wheel = -.5
            return True

        if ev.type == pygame.KEYDOWN:
            for char in ev.unicode:
                code = ord(char)
                if 0 < code < 0x10000:
                    io.add_input_character(code)

            io.keys_down[self._custom_key(ev.key)] = True

        if ev.type == pygame.KEYUP:
            io.keys_down[self._custom_key(ev.key)] = False

        if ev.type in (pygame.KEYDOWN, pygame.KEYUP):
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

        if ev.type == pygame.VIDEORESIZE:
            surface = pygame.display.get_surface()
            # note: pygame does not modify existing surface upon resize, we need to it ourselves.
            pygame.display.set_mode(
                (ev.w, ev.h),
                flags=surface.get_flags(),
            )
            # existing font texture is no longer valid, so we need to refresh it
            self.refresh_font_texture()

            # notify imgui about new window size
            io.display_size = ev.size

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
        if io.delta_time <= 0.0:
            io.delta_time = 1. / 1000.
        self._gui_time = current_time


class OpenGlWrapper(object):
    """This wraps to blit onto a pygame.Surface and rendering ImGui onto an OpenGL screen into a single thing.

    Usage:
    (1) Create a pygame display using the flags from `get_display.flags()`
    (2) Create a wrapper instance from that screen
    (3) Forward events to this wrapper using `process_event()`
    (4) Clear and blit on the buffer provided by wrapper_instance.buffer
    (5) Create the ImGui widgets as usual
    (6) Render everything onto the OpenGL screen using `render()`

    The internal rendering order is: buffer first, imgui second.
    """

    def __init__(self, main_screen: pygame.Surface):
        """Initialize OpenGL and ImGui.
        """
        self.screen = main_screen
        self.size = screen.get_size()
        self.buffer = pygame.Surface(self.size)

        # Setup OpenGL Texture
        OpenGL.GL.glViewport(0, 0, *self.size)
        OpenGL.GL.glDepthRange(0, 1)
        OpenGL.GL.glMatrixMode(OpenGL.GL.GL_PROJECTION)
        OpenGL.GL.glMatrixMode(OpenGL.GL.GL_MODELVIEW)
        OpenGL.GL.glLoadIdentity()
        OpenGL.GL.glShadeModel(OpenGL.GL.GL_SMOOTH)
        OpenGL.GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        OpenGL.GL.glClearDepth(1.0)
        OpenGL.GL.glDisable(OpenGL.GL.GL_DEPTH_TEST)
        OpenGL.GL.glDisable(OpenGL.GL.GL_LIGHTING)
        OpenGL.GL.glDepthFunc(OpenGL.GL.GL_LEQUAL)
        OpenGL.GL.glHint(OpenGL.GL.GL_PERSPECTIVE_CORRECTION_HINT, OpenGL.GL.GL_NICEST)
        OpenGL.GL.glEnable(OpenGL.GL.GL_BLEND)
        self.tex_id = OpenGL.GL.glGenTextures(1)

        # setup ImGui stuff
        imgui.create_context()
        self.impl = PygameRenderer()
        self.io = imgui.get_io()
        self.io.display_size = self.size

    @staticmethod
    def get_display_flags() -> int:
        """Returns the required flags for the pygame display init.
        """
        return pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE

    def process_event(self, ev: pygame.event.Event) -> None:
        """Forwards events to ImGui.
        """
        self.impl.process_event(ev)

    def render(self) -> None:
        """Transforms the given surface into a texture, renders it and draws ImGui widgets on top.
        """
        # upload buffer to texture
        rgb_surface = pygame.image.tostring(self.buffer, 'RGB')
        OpenGL.GL.glBindTexture(OpenGL.GL.GL_TEXTURE_2D, self.tex_id)
        OpenGL.GL.glTexParameteri(OpenGL.GL.GL_TEXTURE_2D, OpenGL.GL.GL_TEXTURE_MAG_FILTER, OpenGL.GL.GL_NEAREST)
        OpenGL.GL.glTexParameteri(OpenGL.GL.GL_TEXTURE_2D, OpenGL.GL.GL_TEXTURE_MIN_FILTER, OpenGL.GL.GL_NEAREST)
        OpenGL.GL.glTexParameteri(OpenGL.GL.GL_TEXTURE_2D, OpenGL.GL.GL_TEXTURE_WRAP_S, OpenGL.GL.GL_CLAMP)
        OpenGL.GL.glTexParameteri(OpenGL.GL.GL_TEXTURE_2D, OpenGL.GL.GL_TEXTURE_WRAP_T, OpenGL.GL.GL_CLAMP)
        OpenGL.GL.glTexImage2D(OpenGL.GL.GL_TEXTURE_2D, 0, OpenGL.GL.GL_RGB, *self.size, 0, OpenGL.GL.GL_RGB,
                               OpenGL.GL.GL_UNSIGNED_BYTE, rgb_surface)
        OpenGL.GL.glGenerateMipmap(OpenGL.GL.GL_TEXTURE_2D)
        OpenGL.GL.glBindTexture(OpenGL.GL.GL_TEXTURE_2D, 0)

        # clear OpenGL screen
        OpenGL.GL.glClear(OpenGL.GL.GL_COLOR_BUFFER_BIT)
        OpenGL.GL.glLoadIdentity()
        OpenGL.GL.glDisable(OpenGL.GL.GL_LIGHTING)
        OpenGL.GL.glEnable(OpenGL.GL.GL_TEXTURE_2D)

        # draw texture onto OpenGL screen
        OpenGL.GL.glBindTexture(OpenGL.GL.GL_TEXTURE_2D, self.tex_id)
        OpenGL.GL.glBegin(OpenGL.GL.GL_QUADS)
        OpenGL.GL.glTexCoord2f(0, 0)
        OpenGL.GL.glVertex2f(-1, 1)
        OpenGL.GL.glTexCoord2f(0, 1)
        OpenGL.GL.glVertex2f(-1, -1)
        OpenGL.GL.glTexCoord2f(1, 1)
        OpenGL.GL.glVertex2f(1, -1)
        OpenGL.GL.glTexCoord2f(1, 0)
        OpenGL.GL.glVertex2f(1, 1)
        OpenGL.GL.glEnd()

        # render imgui stuff to OpenGL screen
        imgui.render()
        self.impl.render(imgui.get_draw_data())


if __name__ == "__main__":
    def demo_ui():
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

    pygame.init()
    size = 800, 600

    screen = pygame.display.set_mode(size, OpenGlWrapper.get_display_flags())
    wrapper = OpenGlWrapper(screen)

    background = pygame.image.load('data/background.png')

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            wrapper.process_event(event)

        demo_ui()

        # regular pygame blit etc.
        wrapper.buffer.fill('black')
        wrapper.buffer.blit(background, (0, 0))

        # draws buffer and ImGui to screen
        wrapper.render()

        # as usual
        pygame.display.flip()
