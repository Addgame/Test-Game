import pygame, sys, datetime, os
from sounds import *
from graphics import *
from clientobjects import *
from networking import *
from clientobjects import *
from utils import *
os.environ['SDL_VIDEO_CENTERED'] = '1'

class ClientClass():
    def __init__(self, name, server_type, screen = None, debug = False):
        self.debug = debug
        self.colored_maps = False
        self.show_hud = True
        self.player_name = name
        #self.player = None
        #self.player = ClientPlayerClass(self, self.player_name)
        self.server_type = server_type
        self.game_state = "login"
        self.load_options()
        try:
            self.log_file = open("..\\data\\client_log.txt", 'a')
        except:
            self.log_file = open("..\\data\\client_log.txt", 'w')
        self.log("Game Client Started")
        self.mouse_visible = False
        self.input_mode = None
        self.set_input_mode("keyboard") #sets to keyboard
        #self.set_input_mode("controller") #attempts to set to controller if possible
        self.clock = pygame.time.Clock()
        self.players = ClientPlayerGroup(self)
        self.projectiles = {}
        self.projectile_cooldown = 0
        self.sound = SoundEngineClass(self)
        self.graphics = GraphicsEngineClass(self, screen)
        self.message_group = MessageGroupClass(self)
        self.chat_box = ChatBoxClass(self)
        self.previous_messages = []
        self.prev_message_num = -1
        self.maps = ClientMapGroup(self)
        self.NONE_ITEM = ClientBaseItemClass(self, 1, "NONE_ITEM", "NONEITEM")
        self.player = ClientPlayerClass(self, self.player_name)
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
        self.get_game_input()
        self.graphics.draw_screen()
        reactor.callLater(1/float(self.options["fps"]), self.game_loop)
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
            self.mouse_visible = True
            self.log("Input mode set to controller")
        elif mode == "keyboard" and self.input_mode != "keyboard":
            self.input_mode = "keyboard"
            pygame.mouse.set_visible(False)
            self.mouse_visible = False
            self.log("Input mode set to keyboard")
    def get_game_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.VIDEORESIZE:
                pass #Add manual resize ability
            elif event.type == pygame.JOYHATMOTION:
                if event.value == (0, 1):
                    self.change_input_type()
            else:
                if self.chat_box.show.get():
                    self.get_chat_input(event)
                else:
                    self.get_game_event_input(event)
        if not self.chat_box.show.get():
            self.get_game_nonevent_input()
        if self.projectile_cooldown > 0:
            self.projectile_cooldown -= 1
    def get_game_event_input(self, event):
        if event.type == pygame.KEYDOWN: #Common event checks
            if event.key == pygame.K_1:
                if self.input_mode == 'keyboard' and self.controller_count:
                    self.set_input_mode("controller")
                elif self.input_mode == 'controller':
                    self.set_input_mode('keyboard')
            elif event.key == pygame.K_2:
                self.graphics.create_display([640, 480])
            elif event.key == pygame.K_3:
                self.graphics.create_display([1366, 768])
            elif event.key == pygame.K_4:
                self.graphics.create_display([1920, 1080])
            elif event.key == pygame.K_5:
                self.respawn()
            elif event.key == pygame.K_6:
                self.graphics.load_projectile_textures()
                self.graphics.load_hud_textures()
                self.graphics.load_block_textures()
                self.graphics.load_player_skins("_all")
            elif event.key == pygame.K_7:
                print(self.player.movement)
            elif event.key == pygame.K_t:
                self.change_input_type()
            elif event.key == pygame.K_SLASH:
                self.change_input_type()
                self.chat_box.text = "/"
                self.chat_box.pos = 1
                self.chat_box.make_image()
            elif event.key == pygame.K_ESCAPE:
                self.quit()
        if self.input_mode == 'keyboard': #Keyboard only event checks
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                    self.set_jump(True)
                elif event.key == pygame.K_a:
                    self.set_move(True, 'left')
                elif event.key == pygame.K_d:
                    self.set_move(True, 'right')
                elif event.key == pygame.K_e:
                    self.player.inventory.show_full.toggle()
                    pygame.mouse.set_visible(not self.mouse_visible)
                    self.mouse_visible = not self.mouse_visible
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
                if not self.player.inventory.show_full.get():
                    self.cursor.update(event.pos[0], event.pos[1])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.network_data_handler.send_packet("click_event", "primary", self.cursor.get_point())
                elif event.button == 3:
                    self.network_data_handler.send_packet("click_event", "secondary", self.cursor.get_point())
                elif event.button == 4:
                    self.player.inventory.selected_slot -= 1
                    if self.player.inventory.selected_slot < 0:
                        self.player.inventory.selected_slot = self.player.inventory.hotbar_size - 1
                    self.network_data_handler.send_packet("slot_selected", self.player.inventory.selected_slot)
                elif event.button == 5:
                    self.player.inventory.selected_slot += 1
                    if self.player.inventory.selected_slot > self.player.inventory.hotbar_size - 1:
                        self.player.inventory.selected_slot = 0
                    self.network_data_handler.send_packet("slot_selected", self.player.inventory.selected_slot)
        elif self.input_mode == 'controller': #Controller only event checks
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.player.inventory.show_full.toggle()
                elif event.button == 5:
                    self.set_crouch(True)
                elif event.button == 4:
                    self.set_sprint(True)
                elif event.button == 6:
                    self.network_data_handler.send_packet("click_event", "primary", self.cursor.get_point())
                elif event.button == 7:
                    self.network_data_handler.send_packet("click_event", "secondary", self.cursor.get_point())
                elif event.button == 3:
                    self.respawn()
                elif event.button == 11:
                    self.cursor.fine_adjust.toggle()
            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 5:
                    self.set_crouch(False)
                elif event.button == 4:
                    self.set_sprint(False)
    def get_game_nonevent_input(self):
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
    def get_chat_input(self, event):
        changed = False
        if event.type == pygame.KEYDOWN:
            #print("BEFORE:  " + str(self.chat_box.pos) + "  " + self.chat_box.text)
            if event.key == pygame.K_ESCAPE:
                self.chat_box.text = ""
                self.chat_box.pos = 0
                changed = True
                self.change_input_type()
            elif event.key == pygame.K_BACKSPACE:
                if self.chat_box.pos:
                    self.prev_message_num = -1
                    self.chat_box.text = self.chat_box.text[:self.chat_box.pos - 1] + self.chat_box.text[self.chat_box.pos:]
                    self.chat_box.pos -= 1
                    changed = True
            elif event.key == pygame.K_DELETE:
                if self.chat_box.pos < len(self.chat_box.text):
                    self.prev_message_num = -1
                    self.chat_box.text = self.chat_box.text[:self.chat_box.pos] + self.chat_box.text[self.chat_box.pos + 1:]
                    changed = True
            elif event.key == pygame.K_UP:
                if len(self.previous_messages) and len(self.previous_messages) > self.prev_message_num + 1:
                    self.prev_message_num += 1
                    self.chat_box.text = self.previous_messages[self.prev_message_num]
                    self.chat_box.pos = len(self.chat_box.text)
                    changed = True
            elif event.key == pygame.K_DOWN:
                if len(self.previous_messages) and self.prev_message_num - 1 >= -1:
                    self.prev_message_num -= 1
                    if self.prev_message_num > -1:
                        self.chat_box.text = self.previous_messages[self.prev_message_num]
                        self.chat_box.pos = len(self.chat_box.text)
                    else:
                        self.chat_box.text = ""
                        self.chat_box.pos = 0
                    changed = True
            elif event.key == pygame.K_LEFT:
                if self.chat_box.pos:
                    self.chat_box.pos -= 1
                    changed = True
            elif event.key == pygame.K_RIGHT:
                if self.chat_box.pos < len(self.chat_box.text):
                    self.chat_box.pos += 1
                    changed = True
            elif event.key == pygame.K_HOME:
                self.chat_box.pos = 0
                changed = True
            elif event.key == pygame.K_END:
                self.chat_box.pos = len(self.chat_box.text)
                changed = True
            elif event.key == pygame.K_RETURN:
                self.previous_messages.insert(0, self.chat_box.text)
                self.chat_box.send()
            elif event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                pass
            else:
                self.prev_message_num = -1
                if len(self.chat_box.text) < self.chat_box.char_limit:
                    character = str(event.unicode)
                    self.chat_box.text = self.chat_box.text[:self.chat_box.pos] + character + self.chat_box.text[self.chat_box.pos:]
                    self.chat_box.pos += 1
                    changed = True
            if changed:
                self.chat_box.make_image()
            #print("AFTER:  " + str(self.chat_box.pos) + "  " + self.chat_box.text)
    def change_input_type(self, set = None):
        if set == None:
            self.message_group.show_all.toggle()
            self.chat_box.show.toggle()
            if self.chat_box.show.get():
                pygame.mouse.set_visible(True)
            else:
                pygame.mouse.set_visible(False)
        else:
            self.message_group.show_all.set(set)
            self.chat_box.show.set(set)
            if self.chat_box.show.get():
                pygame.mouse.set_visible(True)
            else:
                pygame.mouse.set_visible(False)
    def check_commands(self, text):
        value = False
        if text.startswith("/client "):
            value = True
            command_list = text.split()
            try:
                if command_list[1] == "map_color":
                    self.colored_maps = string_to_boolean(command_list[2])
                    for map in self.maps.maps.itervalues():
                        map.create_image()
                elif command_list[1] == "show_hud":
                    self.show_hud = string_to_boolean(command_list[2])
                elif command_list[1] == "fullscreen":
                    if string_to_boolean(command_list[2]):
                        self.graphics.create_display(self.graphics.screen.get_size(), pygame.FULLSCREEN)
                    else:
                        self.graphics.create_display(self.graphics.screen.get_size())
                elif command_list[1] == "music":
                    if command_list[2] == "start":
                        if len(command_list) >= 4:
                            self.sound.play_music(command_list[3])
                        else:
                            self.sound.play_music()
                    elif command_list[2] == "stop":
                        self.sound.stop_music()
                elif command_list[1] == "debug":
                    self.debug = string_to_boolean(command_list[2])
            except:
                self.log("Client Command Execution Failed: " + text, "ERROR")
        return value
    def set_move(self, value, direction):
        self.network_data_handler.send_packet("player_movement_input", {direction: value})
    def set_crouch(self, value):
        self.network_data_handler.send_packet("player_movement_input", {"crouch": value})
    def set_sprint(self, value):
        self.network_data_handler.send_packet("player_movement_input", {"sprint": value})
    def set_jump(self, value):
        self.network_data_handler.send_packet("player_movement_input", {"jump": value})
    def respawn(self):
        self.network_data_handler.send_packet("respawn")

class MessageClass(): #DO BETTER REWRITE OF MESSAGES
    def __init__(self, text, color = BLACK, size = 15, font = 'corbel'):
        self.text = text
        self.color = color
        if self.text.find("%y") > 0:
            self.color = YELLOW
            self.text = self.text.replace("%y", "")
        elif self.text.find("%b") > 0:
            self.color = BLUE
            self.text = self.text.replace("%b", "")
        elif self.text.find("%r") > 0:
            self.color = RED
            self.text = self.text.replace("%r", "")
        elif self.text.find("%g") > 0:
            self.color = GREEN
            self.text = self.text.replace("%g", "")
        self.time = -1
        self.font = font + '-' + str(size)
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
        self.fonts = self.client.graphics.fonts
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
                    message.draw_location[1] = (self.client.graphics.screen.get_height() - 55) - (25*((len(self.messages)-1)-self.messages.index(message)))
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

class ChatBoxClass():
    def __init__(self, client):
        self.client = client
        self.show = Toggle(False)
        self.text = ""
        self.pos = 0
        self.location = []
        self.char_limit = 75
        self.image = None
        self.update_location()
        self.make_image()
    def update_location(self):
        self.location = [5, self.client.graphics.screen.get_height() - 30]
    def make_image(self):
        color = BLACK
        value = self.text[:self.pos] + "|" + self.text[self.pos:]
        self.image = self.client.graphics.fonts["corbel-15"].render("> " + value, True, color)
    def send(self):
        if not self.client.check_commands(self.text):
            self.client.network_data_handler.send_packet("player_message", self.text)
        self.text = ""
        self.pos = 0
        self.make_image()
        self.client.change_input_type()
    def draw(self):
        if self.show.get():
            self.client.graphics.screen.blit(self.image, self.location)

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
            if x_adjust > .15 or x_adjust < -.15:
                if self.fine_adjust.get():
                    x_change = x_adjust * self.adjust_values[0]
                else:
                    x_change = x_adjust * self.adjust_values[1]
            else:
                x_change = 0
            if y_adjust > .15 or y_adjust < -.15:
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
    def get_point(self):
        return [self.point_rect.centerx - (self.client.graphics.screen.get_rect().centerx - 15) + self.client.player.rect.x,\
            self.point_rect.centery - (self.client.graphics.screen.get_rect().centery - 15) + self.client.player.rect.y]
    def draw(self):
        self.client.graphics.screen.blit(self.image, self.rect)

if __name__ == '__main__':
    pygame.init()
    try:
        game_client = ClientClass(sys.argv[1], "multiplayer")
        game_client.start_game_connection(sys.argv[2], sys.argv[3])
    except:
        game_client = ClientClass("Addgame", "multiplayer")
        game_client.start_game_connection('localhost', 8007)
