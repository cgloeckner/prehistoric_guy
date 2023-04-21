# noinspection SpellCheckingInspection
"""
Based on
- imgui's pygame-integration example
    URL: https://github.com/pyimgui/pyimgui/blob/master/doc/examples/integrations_pygame.py
- "How can I blit [...] onto an OpenGL surface"
    URL: https://stackoverflow.com/questions/61396799/how-can-i-blit-my-pygame-game-onto-an-opengl-surface
"""

import pygame
from typing import Optional

import imgui
from imgui.integrations.pygame import PygameRenderer

import OpenGL.GL


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

    def __init__(self, buffer_width: int, buffer_height: int, screen_width: int, screen_height: int,
                 ini_file: Optional[str] = None, log_file: Optional[str] = None):
        """Initialize OpenGL and ImGui.
        """
        self.buffer = pygame.Surface((buffer_width, buffer_height))

        # Setup OpenGL Texture
        OpenGL.GL.glViewport(0, 0, screen_width, screen_height)
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
        self.io.display_size = (screen_width, screen_height)
        self.io.ini_file_name = ini_file
        self.io.log_file_name = log_file

    @staticmethod
    def get_display_flags() -> int:
        """Returns the required flags for the pygame display init.
        """
        return pygame.DOUBLEBUF | pygame.OPENGL

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
        OpenGL.GL.glTexImage2D(OpenGL.GL.GL_TEXTURE_2D, 0, OpenGL.GL.GL_RGB, *self.buffer.get_size(), 0,
                               OpenGL.GL.GL_RGB, OpenGL.GL.GL_UNSIGNED_BYTE, rgb_surface)
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
    float_val = 0.4

    def demo_ui():
        global float_val

        imgui.new_frame()

        imgui.begin("Custom window")
        _, float_val = imgui.input_float('value', float_val, 0.1)
        imgui.text(f'Value: {float_val}')
        imgui.end()

    pygame.init()
    size = 800, 600

    screen = pygame.display.set_mode(size, OpenGlWrapper.get_display_flags())
    wrapper = OpenGlWrapper(*screen.get_size(), *screen.get_size())

    background = pygame.image.load('../data/background.png')

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
