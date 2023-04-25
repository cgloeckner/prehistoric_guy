import pygame
import imgui
import pathlib
from abc import abstractmethod, ABC
from typing import Tuple

from core import paths, translate
from core.imgui_wrapper import OpenGlWrapper


class Engine(object):
    def __init__(self, screen_width: int, screen_height: int):
        """Creates an OpenGL screen and a SDL surface buffer. The OpenGL screen is used for ImGui rendering.
        All 2d drawing options are done with the buffer. Later the buffer content is rendered to screen using OpenGL.
        """
        pygame.init()

        self.paths = paths.DataPath(pathlib.Path.cwd() / 'data')
        self.translate = translate.Match()

        screen_size = (screen_width, screen_height)
        pygame.display.set_mode(screen_size, OpenGlWrapper.get_display_flags())
        self.buffer = pygame.Surface(screen_size)
        self.wrapper = OpenGlWrapper()
        self.clock = pygame.time.Clock()

        self.running = False
        self.is_active = True
        self.fill_color = 'black'
        self.max_fps = 150
        self.num_fps = 0
        self.queue = list()

    def __del__(self):
        pygame.quit()

    def push(self, state) -> None:
        """Adds a state to the queue. The latest state is handled first (LIFO).
        """
        if len(self.queue) > 0:
            self.queue[-1].sleep()

        self.queue.append(state)

    def pop(self) -> None:
        """Removes the latest state, which is currently handled (LIFO).
        This may throw an IndexError if the queue is empty.
        """
        self.queue.pop()

        if len(self.queue) > 0:
            self.queue[-1].reinit()

    def run(self) -> None:
        """Runs the latest state until the app is shutdown by the user input or no state is left.
        """
        self.running = True

        elapsed = 0
        while self.running:
            # grab latest state
            if len(self.queue) == 0:
                return

            state = self.queue[-1]

            # handle all events
            for event in pygame.event.get():
                self.wrapper.process_event(event)
                state.process_event(event)

            # update
            imgui.new_frame()
            state.update(elapsed)

            # draw state
            self.buffer.fill(self.fill_color)
            state.draw()

            # render onto OpenGL window
            self.wrapper.render(self.buffer)
            pygame.display.flip()

            # limit fps
            elapsed = self.clock.tick(self.max_fps)
            self.num_fps = self.clock.get_fps()


class State(ABC):
    def __init__(self, engine: Engine):
        self.engine = engine

    @abstractmethod
    def process_event(self, event: pygame.event.Event) -> None:
        pass

    def sleep(self) -> None:
        """Called when the state is pushed to the stack in favor of another state."""
        pass

    def reinit(self) -> None:
        """Called when the state back to the stack's top."""
        pass

    @abstractmethod
    def update(self, elapsed_ms: int) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass
