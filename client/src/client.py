import pygame, sys, datetime, os
from sounds import *
from graphics import *
from networking import *
from utils import *
os.environ['SDL_VIDEO_CENTERED'] = '1'

class ClientClass():
    def __init__(self, name, server_type, screen = None, debug = False):
        self.debug = debug
        self.player_name = name
        self.server_type = server_type
        self.game_state = "login"
        self.load_options()
        try:
            self.log_file = open("..\\data\\client_log.txt", 'a')
        except:
            self.log_file = open("..\\data\\client_log.txt", 'w')
        self.log("Game Client Started")
        self.input_mode = None
        self.set_input_mode("keyboard") #sets to keyboard
        self.set_input_mode("controller") #attempts to set to controller if possible
        self.clock = pygame.time.Clock()
        self.players = {}
        self.projectiles = {}
        self.projectile_cooldown = 0
        self.message_group = MessageGroupClass(self)
        self.sound = SoundEngineClass(self)
        self.graphics = GraphicsEngineClass(self, screen)
        self.blocks = []       
        self.cursor = CursorClass(self)
        self.network_data_handler = DataHandler(self)
        self.network_connector = None
        self.network_factory = None
        self.network_protocol = None
        self.connected = False
    def start_game_connection(self, ip, port = 8007, timeout = 15):
        factory = GameClientFactory(self)
        self.network_connector = reactor.connectTCP(ip, int(port), factory, timeout)
        self.network_factory = factory
        self.network_protocol = factory.protocol
        reactor.callLater(1, self.game_loop)
        reactor.run()
    def game_loop(self):
        self.get_input()
        self.graphics.draw_screen()
        reactor.callLater(1/float(self.options["fps"]), self.game_loop)
    def add_player(self, name):
        self.players[name] = {"images":None, "current_img":None, "movement":{"left":False,"right":False,"jump":False, "crouch":False, \
            "dead":False, "sprint":False}, "location":[0,0], "health":200}
        self.graphics.load_player_skins(name)
    def load_options(self):
        self.options = {"message_limit": 5, "sound_volume": 1.0, "music_volume": .3, "fps": 30.0}
        try:
            options_file = open("..\\data\\options.txt")
            options_list = options_file.read().split("\n")
            for option in options_list:
                option_pair = option.split(":")
                try:
                    self.options[option_pair[0]] = option_pair[1].strip()
                except KeyError:
                    self.log("Option {} does not exist!".format(option_pair[0]), "ERROR")
            options_file.close()
        except IOError:
            self.log("Options file not found! Creating new one!","ERROR")
            options_file = open("..\\data\\options.txt", 'w')
            options_file.write("message_limit:5\nsound_volume:1.00\nmusic_volume:.30\nfps:30.0")
            options_file.close()
        except:
            self.log("Custom options could not be loaded! Using default options!", "ERROR")
    def log(self, message, type = "INFO"):
        time = str(datetime.datetime.now())
        time_stamp = '[' + time.split('.')[0] + '] [' + type + ']: '
        log_message = time_stamp + message
        print(log_message)
        self.log_file.write(log_message + '\n')
    def quit(self):
        self.network_connector.disconnect()
        reactor.stop()
    def set_input_mode(self, mode):
        self.controller_count = pygame.joystick.get_count()
        if mode == "controller" and self.input_mode != "controller" and self.controller_count > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            self.input_mode = "controller"
            pygame.mouse.set_visible(True)
            self.log("Input mode set to controller")
        elif mode == "keyboard" and self.input_mode != "keyboard":
            self.input_mode = "keyboard"
            pygame.mouse.set_visible(False)
            self.log("Input mode set to keyboard")
    def get_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:#Common event checks
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if self.input_mode == 'keyboard' and self.controller_count:
                        self.set_input_mode("controller")
                    elif self.input_mode == 'controller':
                        self.set_input_mode('keyboard')
                elif event.key == pygame.K_2:
                    pass #self.take_damage(10, 'magic')
                elif event.key == pygame.K_3:
                    self.graphics.create_display([640, 480])
                elif event.key == pygame.K_4:
                    self.graphics.create_display([1366, 768])
                elif event.key == pygame.K_5:
                    self.respawn()
                elif event.key == pygame.K_6:
                    self.sound.play_music()
                elif event.key == pygame.K_7:
                    self.sound.stop_music()
                elif event.key == pygame.K_8:
                    self.graphics.load_projectile_textures()
                    self.graphics.load_hud_textures()
                    self.graphics.load_block_textures()
                    self.graphics.load_player_skins("_all")
                elif event.key == pygame.K_t:
                    self.message_group.show_all.toggle()
                elif event.key == pygame.K_ESCAPE:
                    if self.message_group.show_all.get():
                        self.message_group.show_all.set(False)
                    else:
                        self.quit()
            elif event.type == pygame.VIDEORESIZE:
                pass #TODO: Add manual resize ability
            if self.input_mode == 'keyboard': #Keyboard only event checks
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        self.set_jump(True)
                    elif event.key == pygame.K_a:
                        self.set_move(True, 'left')
                    elif event.key == pygame.K_d:
                        self.set_move(True, 'right')
                    elif event.key == pygame.K_LSHIFT:
                        self.set_crouch(True)
                    elif event.key == pygame.K_LCTRL:
                        self.set_sprint(True)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        self.set_jump(False)
                    elif event.key == pygame.K_a:
                        self.set_move(False, 'left')
                    elif event.key == pygame.K_d:
                        self.set_move(False, 'right')
                    elif event.key == pygame.K_LSHIFT:
                        self.set_crouch(False)
                    elif event.key == pygame.K_LCTRL:
                        self.set_sprint(False)
                elif event.type == pygame.MOUSEMOTION:
                    self.cursor.update(event.pos[0], event.pos[1])
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.launch_projectile()
                    elif event.button == 3:
                        pass #self.place_block()
            elif self.input_mode == 'controller': #Controller only event checks
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 5:
                        self.set_crouch(True)
                    elif event.button == 4:
                        self.set_sprint(True)
                    elif event.button == 6:
                        self.launch_projectile()
                    elif event.button == 7:
                        pass #self.place_block()
                    elif event.button == 3:
                        self.respawn()
                    elif event.button == 11:
                        self.cursor.fine_adjust.toggle()
                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == 5:                    
                        self.set_crouch(False)
                    elif event.button == 4:
                        self.set_sprint(False)
                elif event.type == pygame.JOYHATMOTION:
                    if event.value == (0, 1):
                        self.message_group.show_all.toggle()
        if self.input_mode == 'keyboard': #Keyboard only non-event checks
            pass
        elif self.input_mode == 'controller': #Controller only non-event checks
            leftx = self.controller.get_axis(0)
            if leftx <= -.2:
                self.set_move(True, 'left')
            elif leftx > -.2:
                self.set_move(False, 'left')
            if leftx >= .2:
                self.set_move(True, 'right')
            elif leftx < .2:
                self.set_move(False, 'right')
            lefty = self.controller.get_axis(1)
            if lefty <= -.3:
                self.set_jump(True)
            elif lefty > -.3:
                self.set_jump(False)
            rightx = self.controller.get_axis(2)
            righty = self.controller.get_axis(3)
            self.cursor.update(rightx, righty)
        #if #SET UP TO SEND ALL MOVEMENT UPDATES AT ONCE  #Common non-event checks
        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1
    def set_move(self, value, direction):
        self.network_data_handler.send_packet("player_movement_input", {direction: value})
    def set_crouch(self, value):
        self.network_data_handler.send_packet("player_movement_input", {"crouch": value})
    def set_sprint(self, value):
        self.network_data_handler.send_packet("player_movement_input", {"sprint": value})
    def set_jump(self, value):
        self.network_data_handler.send_packet("player_movement_input", {"jump": value})
    def launch_projectile(self):
        if self.projectile_cooldown < 1:
            self.network_data_handler.send_packet("launch_projectile", self.cursor.get_point())
            self.projectile_cooldown = int(self.clock.get_fps())
    def respawn(self):
        self.network_data_handler.send_packet("respawn")

class MessageClass(): #DO BETTER REWRITE OF MESSAGES
    def __init__(self, text, type = "broadcast", color = BLACK, size = 15, font = 'corbel'):
        self.text = text
        self.time = -1
        self.font = font + '-' + str(size)
        self.color = color
        self.image = None
        self.draw_location = None
    def draw(self, screen, location = None):
        if location == None:
            location = self.draw_location
        screen.blit(self.image, location)

class MessageGroupClass():
    def __init__(self, client):
        self.client = client
        self.message_limit = int(self.client.options["message_limit"])
        self.messages = []
        self.fonts = {"corbel-15": pygame.font.Font(pygame.font.match_font("corbel"), 15)}
        self.show_all = Toggle(False)
        self.update_display = False
        self.update_location = False
    def add_message(self, message):
        self.create_msg_image(message)
        time = int(self.client.clock.get_fps() * 10) #TODO: FIND EASIER WAY TO DO THIS
        if time < 300:
            time = 300
        message.time = time
        self.messages.append(message)
        self.update_display = True
        self.update_location = True
        if len(self.messages) > self.message_limit:
            removed_message = self.messages.pop(0)
    def create_msg_image(self, message):
        message.image = self.fonts[message.font].render(message.text, True, message.color)
        message.draw_location = [5, None]
    def update(self):
        if self.update_display:
            need_update = False
            for message in self.messages:
                if message.time > -1:
                    message.time -= 1
                    need_update = True
                if self.update_location:
                    message.draw_location[1] = (self.client.graphics.screen.get_height() - 30) - (25*((len(self.messages)-1)-self.messages.index(message)))
            if need_update == False:
                self.update_display = False
            if self.update_location == True:
                self.update_location = False
    def clear(self):
        self.messages = []
        self.update_display = False
        self.update_location = False
    def draw(self):
        for message in self.messages:
            if self.show_all.get() or message.time > -1:
                message.draw(self.client.graphics.screen)

class CursorClass():
    def __init__(self, client):
        self.client = client
        self.image = self.client.graphics.get_cursor_textures()
        self.rect = self.image.get_rect(center=self.client.graphics.screen.get_rect().center)
        self.point_rect = pygame.Rect(self.rect.center, (1, 1))
        self.update_point_rect()
        self.fine_adjust = Toggle(False)
        self.adjust_values = [8, 25]
    def update(self, x_adjust, y_adjust):
        if self.client.input_mode == 'keyboard':
            self.rect.x = x_adjust
            self.rect.y = y_adjust
        elif self.client.input_mode == 'controller':
            if x_adjust > .1 or x_adjust < -.1:
                if self.fine_adjust.get():
                    x_change = x_adjust * self.adjust_values[0]
                else:
                    x_change = x_adjust * self.adjust_values[1]
            else:
                x_change = 0
            if y_adjust > .1 or y_adjust < -.1:
                if self.fine_adjust.get():
                    y_change = y_adjust * self.adjust_values[0]
                else:
                    y_change = y_adjust * self.adjust_values[1]
            else:
                y_change = 0
            self.rect.x += x_change
            self.rect.y += y_change
            if self.rect.x < 0:
                self.rect.x = 0
            elif self.rect.x > self.client.graphics.screen.get_width():
                self.rect.x = self.client.graphics.screen.get_width() 
            if self.rect.y < 0:
                self.rect.y = 0
            elif self.rect.y > self.client.graphics.screen.get_height():
                self.rect.y = self.client.graphics.screen.get_height()
        self.update_point_rect()
    def update_point_rect(self):
        self.point_rect.x = self.rect.x + 8
        self.point_rect.y = self.rect.y + 8
    def get_point(self): #TODO: Remove?
        return self.point_rect.center
    def draw(self):
        self.client.graphics.screen.blit(self.image, self.rect)

if __name__ == '__main__':
    pygame.init()
    game_client = ClientClass(sys.argv[1], "multiplayer")
    game_client.start_game_connection(sys.argv[2], sys.argv[3])
