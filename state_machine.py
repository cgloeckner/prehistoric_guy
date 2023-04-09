import pygame
from abc import abstractmethod

from imgui_wrapper import OpenGlWrapper

from constants import *


class Engine(object):
    def __init__(self):
        pygame.init()

        # get native resolution and factor for scaling
        native_width, native_height = pygame.display.get_desktop_sizes()[0]
        native_width //= RESOLUTION_X
        native_height //= RESOLUTION_Y
        # self.ui_scale_factor = max(1, min(native_width, native_height))
        # override it for debugging purpose
        self.ui_scale_factor = 2

        # calculate window resolution and initialize screen
        window_width = RESOLUTION_X * self.ui_scale_factor
        window_height = RESOLUTION_Y * self.ui_scale_factor
        print(f'Resolution: {window_width}x{window_height}; Resize: {self.ui_scale_factor}')
        self.screen = pygame.display.set_mode((window_width, window_height), OpenGlWrapper.get_display_flags())
        self.buffer = pygame.Surface((RESOLUTION_X, RESOLUTION_Y))
        self.wrapper = OpenGlWrapper(self.screen)
        self.clock = pygame.time.Clock()

        self.running = False
        self.fill_color = 'black'
        self.max_fps = 60
        self.queue = list()

    def __del__(self):
        pygame.quit()

    def push(self, state) -> None:
        """Adds a state to the queue. The latest state is handled first (LIFO).
        """
        self.queue.append(state)

    def pop(self) -> None:
        """Removes the latest state, which is currently handled (LIFO).
        This may throw an IndexError if the queue is empty.
        """
        self.queue.pop()

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

            # update and draw
            state.update(elapsed)
            self.buffer.fill(self.fill_color)
            state.draw()
            pygame.display.flip()

            # limit fps
            elapsed = self.clock.tick(self.max_fps)


class State(object):
    def __init__(self, engine: Engine):
        self.engine = engine

    @abstractmethod
    def process_event(self, event: pygame.event.Event) -> None:
        pass

    @abstractmethod
    def update(self, elapsed_ms: int) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass
