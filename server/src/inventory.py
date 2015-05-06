import pygame, math
from items import *
from itemData import *

class InventoryClass():
    def __init__(self, server, owner, num_slot, row_length):
        self.server = server
        self.owner = owner
        if not isinstance(owner, InventoryOwnerClass):
            print("ERROR: Owner not of InventoryOwnerClass!!!")
        self.items = None
        self.num_slot = None
        self.row_length = None
        self.update_size(num_slot)
        self.update_row_length(row_length)
    def reduce_item_stack(self, slot):
        item = self.items[slot]
        item.reduce_count()
        if item.count < 1:
            self.delete_item(slot)
    def update_size(self, num_slot):
        self.items = [self.server.NONE_ITEM] * num_slot
        self.num_slot = num_slot
    def update_row_length(self, new_row_len):
        self.row_length = new_row_len
    def get_item(self, slot_num):
        if slot_num > self.num_slot:
            self.server.log("Attempted to access item in inventory out of range!: " + str(self.owner)\
                + "    " + str(slot_num) + " / " + str(self.num_slot), "ERROR")
        return self.items[slot_num]
    def set_item(self, slot_num, item):
        old_item = self.get_item(slot_num)
        self.items[slot_num] = item
        return old_item
    def delete_item(self, slot_num):
        return self.set_item(slot_num, self.server.NONE_ITEM)
    def items_to_list(self):
        items_list = []
        for item in self.items:
            items_list.append(item.convert_dict())
        return items_list

class PlayerInventoryClass(InventoryClass):
    def __init__(self, server, player, num_slot, row_length, hotbar_size, selected_slot):
        if hotbar_size > row_length:
            hotbar_size = row_length
        InventoryClass.__init__(self, server, player, num_slot, row_length)
        self.hotbar_size = hotbar_size
        self.selected_slot = selected_slot
        self.selected_item = self.server.NONE_ITEM
        self.update_selected(selected_slot)
    def use_item(self, type, location):
        if not self.owner.movement["dead"]:
            if type == "primary":
                if math.sqrt(((location[0] - self.owner.rect.centerx) ** 2) + ((location[1] - self.owner.rect.centery) ** 2)) <= 192:
                    block = self.server.maps.get_block_at(location)
                    if block:
                        block.destroy()
            elif type == "secondary":
                if isinstance(self.selected_item, BlockItemClass):
                    if math.sqrt(((location[0] - self.owner.rect.centerx) ** 2) + ((location[1] - self.owner.rect.centery) ** 2)) <= 192:
                        block = self.selected_item.place(location)
                        if block.placed:
                            self.reduce_item_stack(self.selected_slot)
                            self.update_selected(self.selected_slot)
                            for player in self.server.players:
                                if math.sqrt(((location[0]-player.rect.x) ** 2) + ((location[1]-player.rect.y) ** 2)) <= 300:
                                    self.server.network_data_handler.send_packet(player.get_protocol(), "playsound", "pop")
                elif isinstance(self.selected_item, ProjectileItemClass):
                    if location[0] - self.owner.rect.x > 0:
                        x_factor = 1
                    else:
                        x_factor = -1
                    launch_speed = projectile_data[self.selected_item.internal_name]["speed"]
                    angle = math.atan2(location[1] - self.owner.rect.y, location[0] - self.owner.rect.x)
                    projectile = self.selected_item.launch([self.owner.rect.centerx + 17 * x_factor, self.owner.rect.centery], [30 * math.cos(angle), 30 * math.sin(angle)])
                    self.reduce_item_stack(self.selected_slot)
                    self.update_selected(self.selected_slot)
    def stop_use_item(self, type, location):
        pass
    def reduce_item_stack(self, slot):
        InventoryClass.reduce_item_stack(self, slot)
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_items", self.owner.name, self.items_to_list())
    def update_selected(self, selected_slot = None):
        if selected_slot == None:
            selected_slot = self.selected_slot
        if selected_slot > self.hotbar_size - 1:
            selected_slot = 0
        elif selected_slot < 0:
            selected_slot = self.hotbar_size
        self.selected_slot = selected_slot
        self.selected_item = self.get_item(self.selected_slot)
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_selected_slot", self.owner.name, self.selected_slot)
        self.server.network_data_handler.send_packet_all("player_data_inv_selected_item", self.owner.name, self.selected_item.convert_dict())
    def change_selected(self, change):
        self.update_selected(self.selected_slot + change)
    def update_row_length(self, new_row_len):
        InventoryClass.update_row_length(self, new_row_len)
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_row_length", self.owner.name, self.row_length)
    def update_size(self, num_slot):
        InventoryClass.update_size(self, num_slot)
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_size", self.owner.name, self.num_slot)
    def set_item(self, slot_num, item):
        InventoryClass.set_item(self, slot_num, item)
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_items", self.owner.name, self.items_to_list())
        self.update_selected(self.selected_slot)
    def send_data(self):
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_selected_slot", self.owner.name, self.selected_slot)
        self.server.network_data_handler.send_packet_all("player_data_inv_selected_item", self.owner.name, self.selected_item.convert_dict())
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_row_length", self.owner.name, self.row_length)
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_size", self.owner.name, self.num_slot)
        self.server.network_data_handler.send_packet(self.owner.get_protocol(), "player_data_inv_items", self.owner.name, self.items_to_list())

class InventoryOwnerClass():
    def __init__(self, type):
        self.inventory = None #Should be instance of base class InventoryClass
        self.type = type