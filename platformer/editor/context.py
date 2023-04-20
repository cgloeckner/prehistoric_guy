import pygame
import pathlib
from typing import List

from core import paths
from platformer import physics, renderer

from . import files


class LevelSelection:
    def __init__(self):
        self.platforms: List[physics.Platform] = list()
        self.ladders: List[physics.Ladder] = list()
        self.objects: List[physics.Object] = list()

    def clear(self) -> None:
        self.platforms.clear()
        self.ladders.clear()
        self.objects.clear()


# ----------------------------------------------------------------------------------------------------------------------


class Context:
    def __init__(self, width: int, height: int, p: paths.DataPath):
        self.new_filename = ''
        self.file_status = files.FileStatus()
        self.ctx = physics.Context()
        self.cam = renderer.Camera(width, height)
        self.paths = p

        self.selected = LevelSelection()
        self.hovered = LevelSelection()

        self.reset()

    def reset(self):
        self.file_status.filename = ''
        self.file_status.unsaved_changes = True

        # replace platforms, ladders and objects
        self.ctx.platforms.clear()
        self.ctx.ladders.clear()
        self.ctx.objects.clear()
        self.ctx.create_platform(x=0, y=0, width=10)

        # reset camera
        self.cam.topleft = pygame.math.Vector2(-1, -1)

    def load(self):
        self.file_status.unsaved_changes = False
        full_path = self.get_full_levelname()
        ctx = files.from_xml(files.from_file(full_path))

        files.apply_context(self.ctx, ctx)

        # reset camera
        self.cam.topleft = pygame.math.Vector2()

    def save(self):
        self.file_status.unsaved_changes = False
        full_path = self.get_full_levelname()
        files.to_file(files.to_xml(self.ctx), full_path)

    def get_full_levelname(self) -> pathlib.Path:
        return self.paths.level(self.file_status.filename)

    def update(self, elapsed_ms: int) -> None:
        pass
