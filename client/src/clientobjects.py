import pygame, random
from math import ceil
from colors import *
from utils import *

class ClientPlayerClass(pygame.sprite.Sprite):
    def __init__(self, client, name, location = [0,0], **movementargs):
        pygame.sprite.Sprite.__init__(self)
        self.client = client
        self.name = name
        self.health = 0
        self.inventory = ClientPlayerInventoryClass(self.client, self, 40, 10, 9)
        self.movement = {"left":False,"right":False,"jump":False, "crouch":False, \
            "dead":False, "sprint":False}
        self.size = (31, 64)
        self.rect = pygame.Rect(location, self.size)
        self.current_map = ()
        self.update_location(location)
        self.images = {}
        self.load_images()
        self.current_img = self.images["player"]
    def load_images(self):
        try:
            self.images = {"player": pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\player.png").convert(), \
                "playerCrouch": pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\playerCrouch.png").convert(), \
                "playerCrouchJump": pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\playerCrouchJump.png").convert(), \
                "playerDead": pygame.transform.rotate(pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\player.png"), 90).convert(), \
                "playerJump": pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\playerJump.png").convert()}
        except:
            self.images = {"player": pygame.image.load("..\\data\\textures\\players\\player\\player.png").convert(), \
                "playerCrouch": pygame.image.load("..\\data\\textures\\players\\player\\playerCrouch.png").convert(), \
                "playerCrouchJump": pygame.image.load("..\\data\\textures\\players\\player\\playerCrouchJump.png").convert(), \
                "playerDead": pygame.transform.rotate(pygame.image.load("..\\data\\textures\\players\\player\\player.png"), 90).convert(), \
                "playerJump": pygame.image.load("..\\data\\textures\\players\\player\\playerJump.png").convert()}
    def update_location(self, location):
        self.rect.topleft = location
        self.current_map = (self.rect.x >> 9, self.rect.y >> 9)
    def update_image(self):
        img_name = "player"
        if self.movement["crouch"] == True:
            img_name += "Crouch"
        if self.movement["jump"] == True:
            img_name += "Jump"
        if self.movement["dead"] == True:
            img_name += "Dead"
        self.current_img = self.images[img_name]

class ClientPlayerGroup(pygame.sprite.Group):
    def __init__(self, client):
        pygame.sprite.Group.__init__(self)
        self.client = client
        self.names = []
        self.names_color = {}
    def add_player(self, name, name_color = WHITE):
        player = ClientPlayerClass(self.client, name)
        player.load_images()
        self.names.append(name)
        self.names_color[name] = name_color
        self.add(player)
        if name == self.client.player_name:
            self.client.player = player
    def remove_player(self, name):
        self.name_to_player(name).kill()
        self.names.remove(name)
        self.names_color.pop(name)
    def name_to_player(self, name):
        if not name in self.names:
            return None
        for player in self:
            if player.name == name:
                return player

class ClientBaseItemClass(pygame.sprite.Sprite):
    def __init__(self, client, count, internal_name, display_name):
        pygame.sprite.Sprite.__init__(self)
        self.client = client
        self.count = count
        self.internal_name = internal_name
        self.display_name = display_name
        self.image = None
        self.size = None
        self.create_image()
    def create_image(self):
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA).convert_alpha()

class ClientBlockItemClass(ClientBaseItemClass):
    def __init__(self, client, count, internal_name, display_name):
        ClientBaseItemClass.__init__(self, client, count, internal_name, display_name)
        self.size = self.client.graphics.block_textures[self.internal_name].get_size()
    def create_image(self):
        self.image = self.client.graphics.block_textures[self.internal_name].copy()
        if self.image.get_size() != (24, 24):
            self.image = pygame.transform.scale(self.image, (24, 24))
        number_surface = self.client.graphics.fonts["corbelb-15"].render(str(self.count), True, BLACK)
        draw_loc = [self.image.get_width() - number_surface.get_width(), self.image.get_height() - number_surface.get_height()]
        white_background = pygame.Surface(number_surface.get_size(), pygame.SRCALPHA).convert_alpha()
        white_background.fill(WHITEFADE)
        self.image.blit(white_background, draw_loc)
        self.image.blit(number_surface, draw_loc)

class ClientProjectileItemClass(ClientBaseItemClass):
    def __init__(self, client, count, internal_name, display_name):
        ClientBaseItemClass.__init__(self, client, count, internal_name, display_name)
        self.size = self.client.graphics.projectile_textures[self.internal_name].get_size()
    def create_image(self):
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA).convert_alpha()
        item_img = self.client.graphics.projectile_textures[self.internal_name].copy()
        if item_img.get_width() > 24 or item_img.get_height() > 24:
            item_img = pygame.transform.scale(item_img, (24, 24))
            location = [0,0]
        else:
            location = [12 - item_img.get_width() / 2, 12 - item_img.get_height() / 2]
        self.image.blit(item_img, location)
        number_surface = self.client.graphics.fonts["corbelb-15"].render(str(self.count), True, BLACK)
        draw_loc = [self.image.get_width() - number_surface.get_width(), self.image.get_height() - number_surface.get_height()]
        white_background = pygame.Surface(number_surface.get_size(), pygame.SRCALPHA).convert_alpha()
        white_background.fill(WHITEFADE)
        self.image.blit(white_background, draw_loc)
        self.image.blit(number_surface, draw_loc)

class ClientNormalItemClass(ClientBaseItemClass):
    def __init__(self, client, count, internal_name, display_name):
        ClientBaseItemClass.__init__(self, client, count, internal_name, display_name)
        self.size = self.client.graphics.item_textures[self.internal_name].get_size()
    def create_image(self):
        self.image = self.client.graphics.item_textures[self.internal_name].copy()
        if self.count != 1:
            number_surface = self.client.graphics.fonts["corbelb-15"].render(str(self.count), True, BLACK)
            draw_loc = [self.image.get_width() - number_surface.get_width(), self.image.get_height() - number_surface.get_height()]
            white_background = pygame.Surface(number_surface.get_size(), pygame.SRCALPHA).convert_alpha()
            white_background.fill(WHITEFADE)
            self.image.blit(white_background, draw_loc)
            self.image.blit(number_surface, draw_loc)

class ClientInventoryClass():
    def __init__(self, client, owner, num_slot, row_length):
        self.client = client
        self.owner = owner
        self.items = None
        self.row_length = row_length
        self.num_slot = num_slot
        self.update_size(num_slot)
    def update_size(self, num_slot):
        self.items = [self.client.NONE_ITEM] * num_slot
        self.num_slot = num_slot
    def update_row_length(self, new_row_len):
        self.row_length = new_row_len
    def get_item(self, slot_num):
        if slot_num > self.num_slot:
            self.client.log("Attempted to access item in inventory out of range!: " + str(self.owner)\
                + str(slot_num) + " / " + str(self.num_slot), "ERROR")
        return self.items[slot_num]
    def set_item(self, slot_num, item):
        old_item = self.get_item(slot_num)
        self.items[slot_num] = item
        return old_item
    def delete_item(self, slot_num):
        return self.set_item(slot_num, self.client.NONE_ITEM)
    def items_from_list(self, item_list):
        self.items = []
        for item_dict in item_list:
            if item_dict["type"] == "block":
                item_class = ClientBlockItemClass
            elif item_dict["type"] == "projectile":
                item_class = ClientProjectileItemClass
            elif item_dict["type"] == "normal":
                item_class = ClientNormalItemClass
            else:
                item_class = ClientBaseItemClass
            item_obj = item_class(self.client, item_dict["count"], item_dict["internal_name"], item_dict["display_name"])
            self.items.append(item_obj)

class ClientPlayerInventoryClass(ClientInventoryClass):
    def __init__(self, client, owner, num_slot, row_length, hotbar_size):
        self.hotbar_size = hotbar_size
        ClientInventoryClass.__init__(self, client, owner, num_slot, row_length)
        self.selected_slot = 0
        self.show_full = Toggle(False)
        self.hotbar_background = None
        self.full_background = None
        self.hotbar_item_image = None
        self.full_item_image = None
        self.create_background_images()
        self.create_item_images()
    def create_background_images(self):
        num_row = ceil(float(self.num_slot) / self.row_length)
        hb_num_row = ceil(float(self.hotbar_size) / self.row_length)
        self.hotbar_background = pygame.Surface((36 * self.row_length, 36 * hb_num_row), pygame.SRCALPHA).convert_alpha()
        self.full_background = pygame.Surface((36 * self.row_length, 36 * num_row), pygame.SRCALPHA).convert_alpha()
        for slot in range(self.num_slot):
            draw_loc = [(slot - (self.row_length * int(slot/self.row_length))) * 36, self.full_background.get_height() - (ceil(float(slot + 1) / self.row_length) * 36)]
            if slot < self.hotbar_size:
                hb_draw_loc = [(slot - (self.row_length * int(slot/self.row_length))) * 36, self.hotbar_background.get_height() - (ceil(float(slot + 1) / self.row_length) * 36)]
                self.hotbar_background.blit(self.client.graphics.hud_textures["hotbarslot"], hb_draw_loc)
                self.full_background.blit(self.client.graphics.hud_textures["hotbarslot"], draw_loc)
            else:
                self.full_background.blit(self.client.graphics.hud_textures["inventoryslot"], draw_loc)
    def create_item_images(self):
        num_row = ceil(float(self.num_slot) / self.row_length)
        hb_num_row = ceil(float(self.hotbar_size) / self.row_length)
        self.hotbar_item_image = pygame.Surface((36 * self.row_length, 36 * hb_num_row), pygame.SRCALPHA).convert_alpha()
        self.full_item_image = pygame.Surface((36 * self.row_length, 36 * num_row), pygame.SRCALPHA).convert_alpha()
        for slot in range(self.num_slot):
            if self.items[slot] != self.client.NONE_ITEM:
                draw_loc = [(slot - (self.row_length * int(slot/self.row_length))) * 36 + 4, self.full_item_image.get_height() - (ceil(float(slot + 1) / self.row_length) * 36) + 4]
                if slot < self.hotbar_size:
                    hb_draw_loc = [(slot - (self.row_length * int(slot/self.row_length))) * 36 + 4, self.hotbar_item_image.get_height() - (ceil(float(slot + 1) / self.row_length) * 36) + 4]
                    self.hotbar_item_image.blit(self.items[slot].image, hb_draw_loc)
                    self.full_item_image.blit(self.items[slot].image, draw_loc)
                else:
                    self.full_item_image.blit(self.items[slot].image, draw_loc)
    def draw(self):
        if self.show_full.get():
            loc = [self.client.graphics.screen.get_width() - self.full_background.get_width(),\
                self.client.graphics.screen.get_height() - self.full_background.get_height()]
            self.client.graphics.screen.blit(self.full_background, loc)
            self.client.graphics.screen.blit(self.full_item_image, loc)
        else:
            loc = [self.client.graphics.screen.get_width() - self.hotbar_background.get_width(),\
                self.client.graphics.screen.get_height() - self.hotbar_background.get_height()]
            self.client.graphics.screen.blit(self.hotbar_background, loc)
            self.client.graphics.screen.blit(self.hotbar_item_image, loc)
        self.client.graphics.screen.blit(self.client.graphics.hud_textures["slothighlight"], \
            [self.client.graphics.screen.get_width() - (36 * self.row_length) + ((self.selected_slot - (self.row_length * int(self.selected_slot/self.row_length))) * 36), \
            self.client.graphics.screen.get_height() - 36 * int(ceil(float(self.selected_slot + 1) / self.row_length))])
    def update_size(self, num_slot):
        ClientInventoryClass.update_size(self, num_slot)
        self.create_item_images()
    def update_row_length(self, new_row_len):
        ClientInventoryClass.update_row_length(self, new_row_len)
        self.create_item_images()
    def set_item(self, slot_num, item):
        ClientInventoryClass.set_item(self, slot_num, item)
        self.create_item_images()
    def items_from_list(self, list):
        ClientInventoryClass.items_from_list(self, list)
        self.create_item_images()
    def change_selected_slot(self, change):
        self.set_selected_slot(self.selected_slot + change)
    def set_selected_slot(self, set):
        self.selected_slot = set
        if self.selected_slot > self.hotbar_size - 1:
            self.selected_slot = 0
        elif self.selected_slot < 0:
            self.selected_slot = self.hotbar_size - 1
        self.client.network_data_handler.send_packet("slot_selected", self.selected_slot)
    
class ClientMapGroup():
    def __init__(self, client):
        self.client = client
        self.maps = {}
        self.waiting_maps = []
    def loc_to_map(self, location):
        map_x = location[0] >> 9
        map_y = location[1] >> 9
        x = location[0] - (map_x * self.map_size_x)
        y = location[1] - (map_y * self.map_size_y)
        try:
            return self.maps[(map_x, map_y)], (x, y) #Returns map and location in map
        except:
            self.get_map((map_x, map_y))
            return self.maps[(map_x, map_y)], (x, y)
    def loc_to_map_loc(self, location):
        map_x = location[0] >> 9
        map_y = location[1] >> 9
        x = location[0] - (map_x * self.map_size_x)
        y = location[1] - (map_y * self.map_size_y)
        return (map_x, map_y), (x, y) #Returns map_loc and location "in map"
    def get_map(self, map_loc):
        if map_loc not in self.waiting_maps:
            try:
                return self.maps[map_loc]
            except:
                self.send_get_map_packet(map_loc)
                self.waiting_maps.append(map_loc)
                return None
    def send_get_map_packet(self, location):
        self.client.network_data_handler.send_packet("get_map", location)
    def receive_map(self, map_loc, list):
        if map_loc in self.waiting_maps or map_loc in self.maps:
            map = ClientMapClass(self.client, map_loc, list)
            self.maps[map_loc] = map
            if map_loc in self.waiting_maps:
                self.waiting_maps.remove(map_loc)
    def create_map(self, location, map_list):
        self.maps[location] = ClientMapClass(location, map_list)
    def set_block(self, block):
        map = self.loc_to_map(block.rect.topleft)[0]
        map.map_add_block(block)
    def remove_block(self, data):
        if isinstance(data, BlockClass):
            block = data
            map = self.loc_to_map(block.rect.topleft)[0]
            map.map_remove_block(block)

class ClientMapClass():
    def __init__(self, client, location, list = None):
        self.client = client
        self.map_loc = location
        self.draw_loc = [self.map_loc[0] << 9, self.map_loc[1] << 9]
        self.blocks = pygame.sprite.Group()
        self.image = pygame.surface.Surface((512, 512), pygame.SRCALPHA)
        if list:
            self.from_list(list)
    def from_list(self, list):
        for item in list:
            block = ClientBlockClass(self.client, item["name"], item["location"])
            self.map_add_block(block)
        self.create_image()
    def create_image(self):
        self.image = pygame.surface.Surface((512, 512), pygame.SRCALPHA)
        if not self.client.colored_maps:
            self.image.fill((255, 255, 255, 0))
        else:
            self.image.fill((random.randint(0,255), random.randint(0,255), random.randint(0,255), 127))
        for block in self.blocks:
            self.image.blit(block.image, [block.location[0] - self.draw_loc[0], block.location[1] - self.draw_loc[1]])
        self.image = self.image.convert_alpha()
    def map_add_block(self, block):
        self.blocks.add(block)
        self.create_image()
    def map_remove_block(self, block):
        self.blocks.remove(block)
        self.create_image()

class ClientBlockClass(pygame.sprite.Sprite):
    def __init__(self, client, name, location):
        pygame.sprite.Sprite.__init__(self)
        self.client = client
        self.name = name
        self.location = location
        self.image = None
        self.rect = None
        self.load_texture()
    def load_texture(self):
        self.image = self.client.graphics.block_textures[self.name].convert_alpha()
        self.size = self.image.get_size()

class ClientProjectileClass(pygame.sprite.Sprite):
    pass