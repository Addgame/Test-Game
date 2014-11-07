import pygame
import items
from server import *
from entity import *
from inventory import *

class PlayerClass(EntityClass, InventoryOwnerClass):
    def __init__(self, server, location, name):
        EntityClass.__init__(self, server)
        InventoryOwnerClass.__init__(self, "player")
        self.size = (31, 64)
        self.rect = pygame.Rect(location, self.size)
        self.spawnpoint = [0,0]
        self.name = name
        self.movement = {"left":False, "right":False, "jump":False, "crouch":False, "sprint":False, "speed":5, "dead":False}
        self.attempt_stand = False
        self.attempt_sprint = False
        self.jump_length = 0
        self.jump_limit = 10
        self.health = 200
        self.fall_length = 0
        self.fall_damage = 0
        self.velocity = [0,0]
        self.lock_controls = False
        self.last_damage = "nothing"
        self.damage_lockout = {'mob':0,'block':0}
        self.inventory = PlayerInventoryClass(self.server, self, 40, 10, 9, 0)
        #self.cursor_pos = [0,0]
        self.server.players.add(self)
    def save(self):
        pass
    def convert_dict(self):
        return {"movement": self.movement, "location": [self.rect.x, self.rect.y], "health": self.health, "inventory": self.inventory.convert_dict()}
    def get_protocol(self):
        return self.server.network_factory.protocols[self.name]
    def calc_fall(self):
        acceleration = 9.8
        if self.jump_length < self.jump_limit:
            self.fall_length += 1
        #return 4
        time = 1./30
        fall = self.velocity[1] * time + (.5) * acceleration * (time ** 2)
        self.velocity[1] = self.velocity[1] + acceleration * time
        #print("BEFORE: ",fall)
        fall = int(fall * 100 + 5) #*16 before
        #print("AFTER: ",fall)
        if fall > 30:
            fall = 30
        #print("TRUE AFTER: ",fall)    
        #print(self.fall_length)
        return fall
    def reset_fall(self):
        self.fall_damage = 0
        self.fall_length = 0
        self.velocity[1] = 0
    def update(self):
        if not(self.movement["dead"]):
            temp_rect_center = self.rect.center
            speed = [0,0]
            if self.movement["left"] == True:
                speed[0] -= self.movement["speed"]
            if self.movement["right"] == True:
                speed[0] += self.movement["speed"]
            if self.movement["crouch"] == True:
                speed[0] = int(speed[0] * .75)
            elif self.movement["sprint"] == True:
                speed[0] = int(speed[0] * 1.5)
            self.rect.x += speed[0]
            collisions = self.check_collisions("solid")
            for cblock in collisions:
##                if self.server.maps.damaging in cblock.groups(): #TODO:Move and improve damage block code!!
##                    if self.damage_lockout['block'] <= 0: 
##                        self.take_damage(blockData[cblock.name]["extra"]["damage"], cblock.name)
##                        self.damage_lockout['block'] = 15
                if speed[0] > 0:
                    self.rect.right = cblock.rect.left
                else:
                    self.rect.left = cblock.rect.right
            if self.movement["jump"] == True and self.jump_length == 0:
                self.velocity[1] = -10
            ##speed[1] += self.calc_fall()
            if self.movement["jump"] == True and self.jump_length < self.jump_limit:
                speed[1] -= 8
                self.jump_length += 1
            elif self.movement["jump"] == True and self.jump_length == self.jump_limit:
                self.jump_length += 1
                self.update_movement_input({"jump": False})
            if self.movement["jump"] == False or self.jump_length > self.jump_limit:            
                speed[1] += self.calc_fall()
                if self.fall_length > 25:
                    self.fall_damage = int((self.fall_length - 25) * .75)
                self.jump_length = self.jump_limit #Only if no double jump items
            self.rect.y += speed[1]
            if self.rect.y > 832: #Full body length beyond 768 tall screen
                self.rect.y = -64
            collisions = self.check_collisions("solid")
            for cblock in collisions:
                if speed[1] > 0:
                    self.jump_length = 0
                    self.fall_length = 0
                    self.velocity[1] = 0
                    self.rect.bottom = cblock.rect.top
                    if self.fall_damage > 0 and not self.movement["dead"]:
                        self.take_damage(self.fall_damage, 'fall')
                        self.fall_damage = 0
                else:
                    self.jump_length = self.jump_limit
                    self.velocity[1] = 0
                    self.rect.top = cblock.rect.bottom
            if collisions == [] and self.movement["jump"] == False:
                self.jump_length = self.jump_limit
            if self.damage_lockout['block'] > 0:
                self.damage_lockout['block'] -= 1
            if self.attempt_stand == True:
                if self.set_crouch(False):
                    self.server.network_data_handler.send_packet_all("player_data_movement", self.name, self.movement)
            if self.attempt_sprint == True:
                if self.set_sprint(True):
                    self.server.network_data_handler.send_packet_all("player_data_movement", self.name, self.movement)
            if self.rect.center != temp_rect_center:
                self.server.network_data_handler.send_packet_all("player_data_location", self.name, [self.rect.x, self.rect.y])
    def take_damage(self, amount, kind):
        self.health -= amount #TODO: Adjust damage for items/skills/potions
        self.last_damage = kind
        print(self.name + ": " + str(self.health))
        self.server.network_data_handler.send_packet_all("player_data_health", self.name, self.health)
        if self.health <= 0:
            self.die()
            #print("{} was killed by {}".format(self.name, self.last_damage))
            self.server.network_data_handler.send_packet_all("chat_message", "{} was killed by {}".format(self.name, self.last_damage))
    def die(self):
        self.set_all_movement(False)
        self.lock_controls = True
        self.rect.x -= self.rect.height/2
        self.rect.y += (self.rect.height - self.rect.width)
        self.rect.size = (self.size[1], self.size[0])
        #self.reset_fall()
        self.movement["dead"] = True
        self.server.network_data_handler.send_packet(self.server.network_factory.protocols[self.name], "death")
        self.server.network_data_handler.send_packet_all("player_data_movement", self.name, self.movement)
        self.server.network_data_handler.send_packet_all("player_data_location", self.name, [self.rect.x, self.rect.y])
    def respawn(self):
        self.lock_controls = False
        self.set_jump(False)
        self.health = 200
        self.server.network_data_handler.send_packet_all("player_data_health", self.name, self.health)
        self.reset_fall()
        self.rect.topleft = self.spawnpoint
        self.rect.size = self.size
        self.movement["dead"] = False
        self.server.network_data_handler.send_packet_all("player_data_movement", self.name, self.movement)
        self.server.network_data_handler.send_packet_all("player_data_location", self.name, [self.rect.x, self.rect.y])
    def update_movement_input(self, movement_dict):
        update_location = False
        temp_movement = self.movement.copy()
        for key, value in movement_dict.items():
            if key == "crouch":
                change = self.set_crouch(value)
                if change == True:
                    update_location = True
            elif key == "jump":
                self.set_jump(value)
            elif key == "sprint":
                self.set_sprint(value)
            elif key == "left":
                self.set_move(value, "left")
            elif key == "right":
                self.set_move(value, "right")
        if self.movement != temp_movement:
            self.server.network_data_handler.send_packet_all("player_data_movement", self.name, self.movement)
            if update_location == True:
                self.server.network_data_handler.send_packet_all("player_data_location", self.name, [self.rect.x, self.rect.y])
    def set_crouch(self, value):
        if value == True and self.movement["crouch"] == False and self.lock_controls == False:
            if self.movement["sprint"] == True:
                self.movement["sprint"] = False
                self.attempt_sprint = True
            self.movement["crouch"] = True
            self.rect.height -= 32
            self.rect.y += 32
            return True
        elif value == True and self.movement["crouch"] == True and self.attempt_stand == True:
            self.attempt_stand = False
        elif value == False and self.movement["crouch"] == True:
            self.rect.height += 32
            self.rect.y -= 32
            if self.check_collisions("all") != []:
                self.rect.height -= 32
                self.rect.y += 32
                self.attempt_stand = True
                return False
            self.movement["crouch"] = False
            self.attempt_stand = False
            return True
    def set_jump(self, value):
        if value == True and self.movement["jump"] == False and self.lock_controls == False:
            if self.jump_length == 0:
                self.movement["jump"] = True
        elif value == False and self.movement["jump"] == True:
            self.movement["jump"] = False
            if self.jump_length > 0:
                self.jump_length = self.jump_limit
    def set_sprint(self, value):
        if value == True and self.movement["sprint"] == False and self.movement["crouch"] == False and self.lock_controls == False:
            self.movement["sprint"] = True
            self.attempt_sprint = False
            return True
        elif value == True and self.movement["crouch"] == True and self.attempt_sprint == False:
            self.attempt_sprint = True
        elif value == False and self.attempt_sprint == True:
            self.attempt_sprint = False
        elif value == False and self.movement["sprint"] == True:
            self.movement["sprint"] =  False
    def set_move(self, value, direction):
        if direction == 'left':
            if value == True and self.movement["left"] == False and self.lock_controls == False:
                self.movement["left"] = True
            elif value == False and self.movement["left"] == True:
                self.movement["left"] =  False
        elif direction == 'right':
            if value == True and self.movement["right"] == False and self.lock_controls == False:
                self.movement["right"] = True
            elif value == False and self.movement["right"] == True:
                self.movement["right"] =  False
    def set_all_movement(self, value, override_lock = False):
        overridden = False
        if override_lock == True and self.lock_controls == True:
            self.lock_controls = False
            overridden = True
        self.set_crouch(value)
        self.set_jump(value)
        self.set_sprint(value)
        self.set_move(value, 'left')
        self.set_move(value, 'right')
        self.server.network_data_handler.send_packet_all("player_data_movement", self.name, self.movement)
        if overridden == True:
            self.lock_controls = True