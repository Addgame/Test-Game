import pygame, json, datetime, base64, sys
from colors import *
from gui.base import *
from menus import *
from client import ClientClass
from twisted.internet import reactor

class Game():
    def __init__(self):
        self.version = "0.2.0"
        self.log_file = open("..\\data\\client_log.txt", 'a')
        self.load_options()
        self.create_display(self.options["resolution"])
        self.state = "menus"
        self.login_info = {"username":"", "password":""}
        self.connection_info = {"ip":"", "port":""}
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
        self.temp_screen = pygame.Surface((1280, 720))
        pygame.display.set_caption("Dungeon Derps v." + self.version)
        pygame.display.set_icon(pygame.image.load("..\\data\\textures\\icon.png"))
    def quit(self):
        reactor.stop()
    def run(self):
        self.bg_image = pygame.image.load("..\\data\\textures\\packs\\default\\main_menu_bg.png")
        self.clock = pygame.time.Clock()
        self.menu = Container(self.temp_screen)
        try:
            login_file = open("..\\data\\" + base64.b64encode("login") + ".dat")
            login_data = json.loads(base64.b64decode(login_file.read()))
            login_file.close()
            self.login_info["username"] = login_data[0]
            self.login_info["password"] = base64.b64decode(login_data[1])
        except:
            self.login_info["username"] = "Username"
            self.login_info["password"] = "Password"
        try:
            connection_file = open("..\\data\\" + base64.b64encode("connection") + ".dat")
            connection_data = json.loads(base64.b64decode(connection_file.read()))
            connection_file.close()
            self.connection_info["ip"] = connection_data[0]
            self.connection_info["port"] = connection_data[1]
        except:
            self.connection_info["ip"] = "127.0.0.1"
            self.connection_info["port"] = "8007"
        LoginMenu(self.menu, self.login_info["username"], self.login_info["password"])
        reactor.callLater(0, self.loop)
        reactor.run()
    def loop(self):
        if self.state == "ingame":
            if pygame.event.peek(pygame.USEREVENT):
                self.state = "menus"
                self.menu.empty()
                MainMenu(self.menu)
            self.game_client.game_loop()
            self.loop_call = reactor.callLater(1./self.game_client.options["fps"], self.loop)
        elif self.state == "menus":
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT and (event.name == "login" or event.name == "main_menu"):
                    if event.name == "login":
                        self.login_info = event.data
                    self.menu.empty()
                    MainMenu(self.menu)
                elif event.type == pygame.USEREVENT and event.name == "logout":
                    self.menu.empty()
                    LoginMenu(self.menu, self.login_info["username"], self.login_info["password"])
                elif event.type == pygame.USEREVENT and event.name == "play":
                    self.menu.empty()
                    ConnectMenu(self.menu, self.connection_info["ip"], self.connection_info["port"])
                elif event.type == pygame.USEREVENT and event.name == "connect":
                    self.connection_info = event.data
                    self.game_client = ClientClass(self.login_info["username"], self.login_info["password"], "multiplayer", self.version, self.options, self.screen)
                    self.game_client.start_game_connection(self.connection_info["ip"], self.connection_info["port"])
                    self.game_client.game_loop()
                    self.state = "ingame"
                elif (event.type == pygame.USEREVENT and event.name == "quit") or (event.type == pygame.QUIT)\
                  or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.quit()
                else:
                    self.menu.handle_event(event)
            self.temp_screen.fill(WHITE)
            self.temp_screen.blit(self.bg_image, (0,0))
            self.menu.draw()
            #pygame.transform.scale(self.temp_screen, self.screen.get_size(), self.screen)
            self.screen.blit(self.temp_screen, (0,0))
            pygame.display.update()
            self.clock.tick()
            self.loop_call = reactor.callLater(1./30, self.loop)