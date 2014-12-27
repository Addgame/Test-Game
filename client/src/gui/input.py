import pygame
from colors import *
from .base import *

class InputBox(GuiObject):
    def __init__(self, text = "", char_size = 25, max_length = 99, **params):
        self.text = text
        self.text_color = params.get("text_color", BLACK)
        self.pos = len(text)
        self.font = params.get("font", pygame.font.Font("..\\data\\fonts\\corbel.ttf", 20))
        size = self.font.size("a" * char_size)
        params["size"] = (size[0] + 4, size[1] + 4)
        params["focusable"] = True
        self.bg_color = params.get("bg_color", (191, 161, 121))
        self.border_color = params.get("border_color", BLACK)
        self.max_length = max_length
        GuiObject.__init__(self, **params)
        self.create_bg_image()
        self.update_image()
    def handle_event(self, event):
        changed = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.pos:
                    self.text = self.text[:self.pos - 1] + self.text[self.pos:]
                    self.pos -= 1
                    changed = True
            elif event.key == pygame.K_DELETE:
                if self.pos < len(self.text):
                    self.text = self.text[:self.pos] + self.text[self.pos + 1:]
                    changed = True
            elif event.key == pygame.K_LEFT:
                if self.pos:
                    self.pos -= 1
                    changed = True
            elif event.key == pygame.K_RIGHT:
                if self.pos < len(self.text):
                    self.pos += 1
                    changed = True
            elif event.key == pygame.K_HOME:
                self.pos = 0
                changed = True
            elif event.key == pygame.K_END:
                self.pos = len(self.text)
                changed = True
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                pass
            elif event.key == pygame.K_TAB:
                pass #Go to next GuiObject on screen
            else:
                if len(self.text) < self.max_length:
                    char = str(event.unicode)
                    self.text = self.text[:self.pos] + char + self.text[self.pos:]
                    self.pos += 1
                    changed = True
        if changed:
            self.update_image()
    def click(self, pos):
        if self.container:
            self.container.set_focus(self)
    def gain_focus(self):
        self.bg_color = (251, 230, 204)
        self.create_bg_image()
        self.update_image()
    def lose_focus(self):
        self.bg_color = (191, 161, 121)
        self.create_bg_image()
        self.update_image()
    def create_bg_image(self):
        self.bg_image = pygame.Surface((self.rect.width + 4, self.rect.height + 4))
        self.bg_image.fill(self.border_color)
        self.bg_image.fill(self.bg_color, pygame.Rect(3, 3, self.rect.width - 2, self.rect.height - 2))
    def update_image(self):
        self.image = pygame.Surface(self.bg_image.get_rect().size, pygame.SRCALPHA)
        self.image.blit(self.bg_image, (0,0))
        self.image.blit(self.font.render(self.text, True, self.text_color), (6, 6))

class PasswordInputBox(InputBox):
    def update_image(self):
        self.image = pygame.Surface(self.bg_image.get_rect().size, pygame.SRCALPHA)
        self.image.blit(self.bg_image, (0,0))
        self.image.blit(self.font.render('*' * len(self.text), True, self.text_color), (4, 4))