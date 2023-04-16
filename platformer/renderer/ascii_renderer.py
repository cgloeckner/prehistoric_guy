import pygame
from dataclasses import dataclass
from typing import List, Tuple

from platformer import physics
from platformer.renderer import base


@dataclass
class AsciiMapping:
    empty: str = '.'
    filled: str = 'X'
    platform: str = '_'
    ladder: str = '#'
    object: str = 'o'
    actor: str = 'A'
    projectile: str = '*'


class AsciiRenderer(base.Renderer):

    def __init__(self, canvas_size: pygame.math.Vector2, context: physics.Context, mapping: AsciiMapping):
        self.canvas_size = canvas_size
        self.context = context
        self.mapping = mapping
        self.buffer: List[List[str]]

        self._clear_buffer()

    def _clear_buffer(self):
        self.buffer = list()
        for y in range(int(self.canvas_size.y)):
            self.buffer.append([self.mapping.empty] * int(self.canvas_size.x))

    def update(self, elapsed_ms: int) -> None:
        pass

    def world_coord_to_index(self, pos: pygame.math.Vector2) -> Tuple[int, int]:
        x = int(pos.x)
        y = int(self.canvas_size.y - pos.y)
        return x, y

    def draw_platform(self, platform: physics.Platform) -> None:
        x, y = self.world_coord_to_index(platform.pos)

        # filled texture
        for h in range(platform.height):
            if 0 <= y + h + 1 < self.canvas_size.y:
                for w in range(platform.width):
                    if 0 <= x - w + 1 < self.canvas_size.x:
                        self.buffer[y + h + 1][x - w + 1] = self.mapping.filled

        if 0 <= y < self.canvas_size.y:
            for w in range(platform.width):
                if 0 <= x - w + 1 < self.canvas_size.x:
                    self.buffer[y][x - w + 1] = self.mapping.platform

    def draw_ladder(self, ladder: physics.Ladder) -> None:
        x, y = self.world_coord_to_index(ladder.pos)

        if 0 <= x < self.canvas_size.x:
            for h in range(ladder.height):
                if 0 <= y - h - 1 < self.canvas_size.y:
                    self.buffer[y - h - 1][x] = self.mapping.ladder

    def draw_object(self, obj: physics.Object) -> None:
        x, y = self.world_coord_to_index(obj.pos)
        self.buffer[y][x] = self.mapping.object

    def draw_projectile(self, projectile: physics.Projectile) -> None:
        x, y = self.world_coord_to_index(projectile.pos)
        self.buffer[y][x] = self.mapping.projectile

    def draw_actor(self, obj: physics.Actor) -> None:
        x, y = self.world_coord_to_index(obj.pos)
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
    context = physics.Context()
    context.create_platform(x=1, y=3, width=3, height=2)
    context.create_platform(x=8, y=3, width=4)
    context.create_platform(x=8, y=5, width=2)
    context.create_platform(x=1, y=5, width=3)
    context.create_ladder(x=8, y=2, height=2)
    context.create_object(x=1, y=3, object_type=physics.ObjectType.FOOD)
    context.create_actor(1, x=7, y=5)
    context.create_projectile(x=5, y=5)

    mapping = AsciiMapping()
    r = AsciiRenderer(pygame.math.Vector2(10, 6), context, mapping)
    r.draw()

    out = ''
    for line in r.buffer:
        for sym in line:
            out += sym
        out += '\n'
    print(out)
