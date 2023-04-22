import pygame
import unittest

from core import resources


def color_to_hex(color: pygame.Color) -> str:
    hex_string = "#{0:02x}{1:02x}{2:02x}".format(
        color.r,
        color.g,
        color.b,
    )
    return hex_string


class ResourcesTest(unittest.TestCase):
    def setUp(self):
        pygame.init()

    def tearDown(self):
        pygame.quit()

    # --- fill_pixels --------------------------------------------------------------------------------------------------

    def test__fill_pixels(self):
        surface = pygame.Surface((5, 5), flags=pygame.SRCALPHA)
        green_rect = pygame.Rect(1, 1, 2, 1)
        pygame.draw.rect(surface, 'green', green_rect)

        color = pygame.Color('black')
        color.hsla = 180, 76, 50, 100
        hex_str = color_to_hex(color)

        resources.fill_pixels(surface, color)

        pixels = pygame.PixelArray(surface)
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                if pixels[x, y] & 0xff000000 == 0:
                    # ignore transparent pixels
                    continue

                hex_ = color_to_hex(surface.unmap_rgb(pixels[x, y]))
                self.assertEqual(hex_, hex_str)
