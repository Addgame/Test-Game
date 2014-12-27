import pygame, json, datetime
from colors import *
from gui.base import *
from menus import *
import base64, json

class Game():
    def __init__(self):
        self.version = "0.2.0"
        self.log_file = open("..\\data\\client_log.txt", 'a')
        self.load_options()
        self.create_display(self.options["resolution"])
        pygame.key.set_repeat(500, 50)
    def load_options(self):
        self.options = {"message_limit": 5, "sound_volume": 1.0, "music_volume": .3, "fps": 30.0, "resolution": [1280, 720]}
        try:
            options_file = open("..\\data\\options.txt")
            self.options = json.load(options_file)
            options_file.close()
        except IOError:
            self.log("Options file not found! Creating new one!","ERROR")
            options_file = open("..\\data\\options.txt", 'w')
            json.dump(self.options, options_file, indent = 4)
            options_file.close()
        except:
            self.log("Custom options could not be loaded! Using default options!", "ERROR")
    def set_option(self, key, value):
        self.options[key] = value
        options_file = open("..\\data\\options.txt", 'w')
        json.dump(options_file, self.options, indent = 4)
        options_file.close()
    def log(self, message, type = "INFO"):
        time = str(datetime.datetime.now())
        time_stamp = '[' + time.split('.')[0] + '] [' + type + ']: '
        log_message = time_stamp + message
        print(log_message)
        self.log_file.write(log_message + '\n')
    def create_display(self, size, flags = 0):
        self.screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("Dungeon Derps v." + self.version)
        pygame.display.set_icon(pygame.image.load("..\\data\\textures\\icon.png"))
    def quit(self):
        pass
    def run(self):
        bg_image = pygame.image.load("..\\data\\textures\\packs\\default\\main_menu_bg.png")
        timer = pygame.time.Clock()
        menu = Container(self.screen)
        try:
            data_file = open("..\\data\\" + base64.b64encode("player") + ".dat")
            data = json.loads(base64.b64decode(data_file.read()))
            data_file.close()
            username = data[0]
            password = base64.b64decode(data[1])
        except:
            username = "Username"
            password = "Password"
        LoginMenu(menu, username, password)
        while True:
            for event in pygame.event.get():
                menu.handle_event(event)
            self.screen.fill(WHITE)
            self.screen.blit(bg_image, (0,0))
            menu.draw()
            pygame.display.update()
            timer.tick(30)