import pygame
from pygame.sprite import Sprite
import pygame.freetype
from pygame.rect import Rect

"""
pygame doesn't really have ui things, so a class to make buttons and stuff.
probably not very efficient but i did it like this for some reason :')
"""


class UIElement(Sprite):

    def __init__(self, center_pos, text, font_size, bg_rgb, high_bg_rgb, text_rgb, action = None):
        """
        Args:
            center_position - tuple (x, y)
            text - string of text to write
            font_size - int
            bg_rgb (background colour) - tuple (r, g, b)
            text_rgb (text colour) - tuple (r, g, b)
        """

        self.mouse_over = False

        default_img = self.create_surface_with_text(text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb)
        highlighted_img = self.create_surface_with_text(text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=high_bg_rgb)

        self.images = [default_img, highlighted_img]
        self.rects = [default_img.get_rect(center=center_pos), highlighted_img.get_rect(center=center_pos)]

        self.action = action

        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    # updates the mouse_over variable and returns the button's action value when clicked
    def update(self, mouse_pos, mouse_up):

        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    # draws element onto a surface
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    # returns surface w/ text written on top
    def create_surface_with_text(self, text, font_size, text_rgb, bg_rgb):
        font = pygame.freetype.SysFont("Courier", font_size, bold=True)
        surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
        return surface.convert_alpha()


