import pygame, sys, datetime, os, json
from sounds import *
from graphics import *
from clientobjects import *
from networking import *
from clientobjects import *
from utils import *
os.environ['SDL_VIDEO_CENTERED'] = '1'

class ClientClass():
    def __init__(self, server_type):
        self.version = "0.2.0"
        self.log_file = open("..\\data\\client_log.txt", 'a')
        self.load_options()
        self.state = "menus"
        self.login_info = {"username":"", "password":""}
        self.connection_info = {"ip":"", "port":""}
        pygame.key.set_repeat(500, 50)
        self.debug = debug
        self.colored_maps = False
        self.show_hud = True
        self.show_list = False
        self.player_name = ""
        self.server_type = server_type
        self.log("Game Client Started")
        self.mouse_visible = False
        self.input_mode = None
        self.set_input_mode("keyboard") #sets to keyboard
        #self.set_input_mode("controller") #attempts to set to controller if possible
        self.clock = pygame.time.Clock()
        self.sound = SoundEngineClass(self)
        self.graphics = GraphicsEngineClass(self, screen, self.options["resolution"])
        self.players = None
        self.projectiles = None
        self.message_group = None
        self.chat_box = None
        self.previous_messages = None
        self.prev_message_num = None
        self.maps = None
        self.NONE_ITEM = None
        self.player = None
        self.movement_changes = None
        self.cursor = None
        self.network_data_handler = None
        self.network_connector = None
        self.network_factory = None
        self.network_protocol = None
        self.connected = False
        self.disconnecting = False
    def a__init__(self, server_type, version, options = None, screen = None, debug = False):
        self.version = "0.2.0"
        self.log_file = open("..\\data\\client_log.txt", 'a')
        self.load_options()
##        self.create_display(self.options["resolution"])
        self.state = "menus"
        self.login_info = {"username":"", "password":""}
        self.connection_info = {"ip":"", "port":""}
        pygame.key.set_repeat(500, 50)
        self.debug = debug
        self.colored_maps = False
        self.show_hud = True
        self.show_list = False
        self.player_name = name
        self.password = str(password.__hash__())
        self.server_type = server_type
        self.game_state = "login"
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
        self.graphics = GraphicsEngineClass(self, screen, self.options["resolution"])
        self.message_group = MessageGroupClass(self)
        self.chat_box = ChatBoxClass(self)
        self.previous_messages = []
        self.prev_message_num = -1
        self.maps = ClientMapGroup(self)
        self.NONE_ITEM = ClientBaseItemClass(self, 1, "NONE_ITEM", "NONE_ITEM")
        self.player = ClientPlayerClass(self, self.player_name)
        self.movement_changes = {}
        self.cursor = CursorClass(self)
        self.network_data_handler = DataHandler(self)
        self.network_connector = None
        self.network_factory = None
        self.network_protocol = None
        self.connected = False
        self.disconnecting = False
    def start_game_connection(self, ip, port = 8007, timeout = 15):
        self.players = ClientPlayerGroup(self)
        self.projectiles = ClientProjectileGroup(Self)
        self.message_group = MessageGroupClass(self)
        self.chat_box = ChatBoxClass(self)
        self.previous_messages = []
        self.prev_message_num = -1
        self.maps = ClientMapGroup(self)
        self.NONE_ITEM = ClientBaseItemClass(self, 1, "NONE_ITEM", "NONE_ITEM")
        self.player = ClientPlayerClass(self, self.player_name)
        self.movement_changes = {}
        self.cursor = Cursor(self)
        self.network_data_handler = DataHandler(self)
        self.network_factory = GameClientFactory(self)
        self.network_connector = reactor.connectTCP(ip, int(port), self.network_factory, timeout)
        self.network_protocol = factory.protocol
        #reactor.callLater(1, self.game_loop)
    def game_loop(self):
        if self.connected:
            self.get_game_input()
        self.graphics.draw_screen()
        if self.movement_changes:
            self.network_data_handler.send_packet("player_movement_input", self.movement_changes)
            self.movement_changes = {}
        if self.game_state != "quitting":
            pass
            #self.delayed_call = reactor.callLater(1/float(self.options["fps"]), self.game_loop)
    def load_options(self):
        self.options = {"message_limit": 5, "sound_volume": 1.0, "music_volume": .3, "fps": 30.0, "resolution": [1280, 720], "show_fps": False}
        try:
            options_file = open("..\\data\\options.txt")
            options_list = options_file.read().split("\n")
            for option in options_list:
                option_pair = option.split(":")
                try:
                    value = option_pair[1].strip()
                    if value.startswith("["):
                        value = json.loads(value) #self.option_string_to_list(value)
                    self.options[option_pair[0]] = value
                except KeyError:
                    self.log("Option {} does not exist!".format(option_pair[0]), "ERROR")
            options_file.close()
        except IOError:
            self.log("Options file not found! Creating new one!","ERROR")
            options_file = open("..\\data\\options.txt", 'w')
            options_file.write("message_limit:5\nsound_volume:1.00\nmusic_volume:.30\nfps:30.0\nresolution:[1280,720]")
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
        reactor.stop()
    def disconnect(self):
        self.log("Game Client Closed!")
        self.disconnecting = True
        self.network_connector.disconnect()
        pygame.mouse.set_visible(True)
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, name = "menus"))
        self.game_state == "quitting"
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
                self.disconnect()
                self.quit()
            elif event.type == pygame.VIDEORESIZE:
                pass #Add manual resize ability
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] == 1:
                    self.change_input_type()
                elif event.value[0]:
                    self.player.inventory.change_selected_slot(event.value[0])
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
                self.graphics.create_display([1280, 720])
            elif event.key == pygame.K_4:
                self.graphics.create_display([1366, 768])
            elif event.key == pygame.K_5:
                self.graphics.create_display([1600, 900])
            elif event.key == pygame.K_6:
                self.graphics.create_display([1920, 1080])
            elif event.key == pygame.K_7:
                self.respawn()
            elif event.key == pygame.K_8:
                self.graphics.load_projectile_textures()
                self.graphics.load_hud_textures()
                self.graphics.load_block_textures()
                self.graphics.load_player_skins("_all")
            elif event.key == pygame.K_t:
                self.change_input_type()
            elif event.key == pygame.K_SLASH:
                self.change_input_type()
                self.chat_box.text = "/"
                self.chat_box.pos = 1
                self.chat_box.make_image()
            elif event.key == pygame.K_ESCAPE:
                if self.player.inventory.show_full.get():
                    self.change_inventory_state(False)
                else:
                    self.disconnect()
        if self.input_mode == 'keyboard': #Keyboard only event checks
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                    self.set_jump(True)
                elif event.key == pygame.K_a:
                    self.set_move(True, 'left')
                elif event.key == pygame.K_d:
                    self.set_move(True, 'right')
                elif event.key == pygame.K_e:
                    self.change_inventory_state()
                elif event.key == pygame.K_LSHIFT:
                    self.set_crouch(True)
                elif event.key == pygame.K_LCTRL:
                    self.set_sprint(True)
                elif event.key == pygame.K_TAB:
                    self.show_list = True
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
                elif event.key == pygame.K_TAB:
                    self.show_list = False
            elif event.type == pygame.MOUSEMOTION:
                if not self.player.inventory.show_full.get():
                    self.cursor.update(event.pos[0], event.pos[1])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.network_data_handler.send_packet("click_event", "primary", self.cursor.get_point())
                elif event.button == 3:
                    self.network_data_handler.send_packet("click_event", "secondary", self.cursor.get_point())
                elif event.button == 4:
                    self.player.inventory.change_selected_slot(-1)
                elif event.button == 5:
                    self.player.inventory.change_selected_slot(1)
                elif event.button == 7:
                    self.set_sprint(True)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.network_data_handler.send_packet("release_event", "primary", self.cursor.get_point())
                elif event.button == 3:
                    self.network_data_handler.send_packet("release_event", "secondary", self.cursor.get_point())
                elif event.button == 7:
                    self.set_sprint(False)
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
                self.prev_message_num = -1
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
                if len(self.previous_messages) == 0 or self.chat_box.text != self.previous_messages[0]:
                    self.previous_messages.insert(0, self.chat_box.text)
                self.prev_message_num = -1
                self.chat_box.send()
            elif event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                pass
            elif event.key == pygame.K_TAB:
                self.chat_box.text = self.chat_box.text[:self.chat_box.pos] + "    " + self.chat_box.text[self.chat_box.pos:]
                self.chat_box.pos += 4
                changed = True
            elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                pass
            else:
                self.prev_message_num = -1
                if event.unicode == '\x16': #Paste
                    data = get_clipboard()
                    if len(self.chat_box.text + data) > self.chat_box.char_limit:
                        data = data[:self.chat_box.char_limit - len(self.chat_box.text)]
                    self.chat_box.text = self.chat_box.text[:self.chat_box.pos] + data + self.chat_box.text[self.chat_box.pos:]
                    self.chat_box.pos += len(data)
                    changed = True
                elif event.unicode == '\x03': #Copy
                    set_clipboard(self.chat_box.text)
                elif event.unicode == '\x18': #Cut
                    set_clipboard(self.chat_box.text)
                    self.chat_box.text = ""
                    self.chat_box.pos = 0
                    changed = True
                else:
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
                self.set_all_movement(False)
                pygame.key.set_repeat(500, 50)
            else:
                pygame.mouse.set_visible(False)
                pygame.key.set_repeat()
        else:
            self.message_group.show_all.set(set)
            self.chat_box.show.set(set)
            if self.chat_box.show.get():
                pygame.mouse.set_visible(True)
                self.set_all_movement(False)
            else:
                pygame.mouse.set_visible(False)
    def change_inventory_state(self, set = None):
        if set == None:
            self.player.inventory.show_full.toggle()
            pygame.mouse.set_visible(not self.mouse_visible)
            self.mouse_visible = not self.mouse_visible
        else:
            self.player.inventory.show_full.set(set)
            pygame.mouse.set_visible(not self.mouse_visible)
            self.mouse_visible = not self.mouse_visible
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
                elif command_list[1] == "show_fps":
                    if len(command_list) > 2:
                        self.show_fps = string_to_boolean(command_list[2])
                    else:
                        self.message_group.add_message(MessageClass("Show FPS: " + str(self.show_fps)))
                elif command_list[1] == "fullscreen":
                    if string_to_boolean(command_list[2]):
                        self.graphics.create_display(self.graphics.screen.get_size(), pygame.FULLSCREEN)
                    else:
                        self.graphics.create_display(self.graphics.screen.get_size())
                elif command_list[1] == "texture_dir":
                    self.graphics.set_texture_directory(command_list[2])
                elif command_list[1] == "mute":
                    self.sound.mute()
                elif command_list[1] == "unmute":
                    self.sound.unmute()
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
        if self.player.movement[direction] != value:
            self.player.movement[direction] = value
            self.movement_changes[direction] = value
    def set_crouch(self, value):
        if self.player.movement["crouch"] != value:
            self.player.movement["crouch"] = value
            self.movement_changes["crouch"] = value
    def set_sprint(self, value):
        if self.player.movement["sprint"] != value:
            self.player.movement["sprint"] = value
            self.movement_changes["sprint"] = value
    def set_jump(self, value):
        if self.player.movement["jump"] != value:
            self.player.movement["jump"] = value
            self.movement_changes["jump"] = value
    def set_all_movement(self, value): #Even used?
        self.network_data_handler.send_packet("player_movement_input", \
            {"left": value, "right": value, "crouch": value, "sprint": value, "jump": value})
    def respawn(self):
        self.network_data_handler.send_packet("respawn")

if __name__ == '__main__':
    pygame.init()
    try:
        name = sys.argv[1]
        ip = sys.argv[2]
        port = sys.argv[3]
    except:
        name = "Addgame"
        ip = 'localhost'
        port = 8007
    game_client = ClientClass(name, "multiplayer")
    game_client.start_game_connection(ip, port)