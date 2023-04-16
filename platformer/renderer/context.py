import pygame

from platformer.physics import Platform


class PygameContext:
    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.platforms = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()
        self.objects = pygame.sprite.Group()
        self.actors = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()

    def add_platform(self, platform: Platform) -> pygame.sprite.Sprite:
        sprite = pygame.sprite.Sprite()
        sprite.parent = platform
        sprite.add(self.platforms)
        return sprite

    # FIXME: more factory methods
    # FIXME: update logic to renew sprite positions and maybe also clip rectangles
