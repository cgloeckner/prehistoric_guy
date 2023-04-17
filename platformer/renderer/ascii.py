import pygame
from dataclasses import dataclass
from typing import List, Tuple

from platformer import physics
from platformer.renderer import base


@dataclass
class Mapping:
    empty: str = '.'
    filled: str = 'X'
    platform: str = '_'
    ladder: str = '#'
    object: str = 'o'
    actor: str = 'A'
    projectile: str = '*'


class AsciiRenderer(base.Renderer):

    def __init__(self, camera: base.Camera, context: physics.Context):
        super().__init__(camera)
        self.context = context
        self.mapping = Mapping()
        self.buffer: List[List[str]]

        self._clear_buffer()

    def _clear_buffer(self):
        self.buffer = list()
        for y in range(self.camera.height):
            self.buffer.append([self.mapping.empty] * self.camera.width)

    def update(self, elapsed_ms: int) -> None:
        pass

    def world_coord_to_index(self, pos: pygame.math.Vector2) -> Tuple[int, int]:
        pos.x = int(pos.x)
        pos.y = int(pos.y)
        cam_pos = self.camera.world2cam_coord(pos)
        pos.y = self.camera.height - cam_pos.y
        return int(pos.x), int(pos.y)

    def draw_platform(self, platform: physics.Platform) -> None:
        x, y = self.world_coord_to_index(platform.pos)

        # filled texture
        for h in range(platform.height):
            if 0 <= y - h - 1 < self.camera.height:
                for w in range(platform.width):
                    if 0 <= x + w < self.camera.width:
                        self.buffer[y - h - 1][x + w] = self.mapping.filled

        if 0 <= y - platform.height - 1 < self.camera.height:
            for w in range(platform.width):
                if 0 <= x + w < self.camera.width:
                    self.buffer[y - platform.height - 1][x + w] = self.mapping.platform

    def draw_ladder(self, ladder: physics.Ladder) -> None:
        x, y = self.world_coord_to_index(ladder.pos)

        if 0 <= x < self.camera.width:
            for h in range(ladder.height):
                if 0 <= y - h - 1 < self.camera.height:
                    self.buffer[y - h - 1][x] = self.mapping.ladder

    def draw_object(self, obj: physics.Object) -> None:
        x, y = self.world_coord_to_index(obj.pos)
        self.buffer[y][x] = self.mapping.object

    def draw_projectile(self, projectile: physics.Projectile) -> None:
        x, y = self.world_coord_to_index(projectile.pos)
        self.buffer[y][x] = self.mapping.projectile

    def draw_actor(self, actor: physics.Actor) -> None:
        x, y = self.world_coord_to_index(actor.pos)
        self.buffer[y][x] = self.mapping.actor

    def draw(self) -> None:
        self._clear_buffer()

        for platform in self.context.platforms:
            self.draw_platform(platform)

        for ladder in self.context.ladders:
            self.draw_ladder(ladder)

        for obj in self.context.objects:
            self.draw_object(obj)

        for projectile in self.context.projectiles:
            self.draw_projectile(projectile)

        for actor in self.context.actors:
            self.draw_actor(actor)


if __name__ == '__main__':
    ctx = physics.Context()
    ctx.create_platform(x=1, y=0, width=3, height=2)
    ctx.create_platform(x=8, y=3, width=4)
    ctx.create_platform(x=7, y=5, width=2)
    ctx.create_platform(x=1, y=5, width=3)
    ctx.create_ladder(x=9, y=3, height=2)
    ctx.create_object(x=1.5, y=3, object_type=physics.ObjectType.FOOD)
    ctx.create_actor(1, x=8.5, y=5)
    ctx.create_projectile(2, x=6.5, y=5.5)

    cam = base.Camera(10, 6)
    #cam.center.x += -1.0

    r = AsciiRenderer(cam, ctx)
    r.draw()

    out = ''
    for line in r.buffer:
        for sym in line:
            out += sym
        out += '\n'
    print(out)
