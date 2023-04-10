import pygame


def progress_bar(target: pygame.Surface, x: int, y: int, width: int, height: int, progress: float,
                 border_width: int = 1, box_color: pygame.Color = pygame.Color('black'),
                 bar_color: pygame.Color = pygame.Color('white'), centered: bool = True) -> None:
    if centered:
        x -= (width + 2 * border_width) // 2
        y -= (height + 2 * border_width) // 2

    pygame.draw.rect(target, box_color, (x, y, width + 2 * border_width, height + 2 * border_width))
    pygame.draw.rect(target, bar_color, (x+1, y+1, width * progress, height))
