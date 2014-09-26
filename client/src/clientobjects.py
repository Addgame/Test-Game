import pygame

class ClientPlayerClass(pygame.sprite.Sprite):
    def __init__(self, name, location = [0,0], **movementargs):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.health = 0
        self.movement = {"left":False,"right":False,"jump":False, "crouch":False, \
            "dead":False, "sprint":False}
        self.location = location
        self.images = {}
        self.load_images()
        self.current_img = self.images["player"]
    def load_images(self):
        self.images = {"player": pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\player.png"), \
            "playerCrouch": pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\playerCrouch.png"), \
            "playerCrouchJump": pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\playerCrouchJump.png"), \
            "playerDead": pygame.transform.rotate(pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\player.png"), 90), \
            "playerJump": pygame.image.load("..\\data\\textures\\players\\" + self.name + "\\playerJump.png")}
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
    def add_player(self, name):
        player = ClientPlayerClass(name)
        player.load_images()
        self.names.append(name)
        self.add(player)
        if name == self.client.player_name:
            self.client.player = player
    def remove_player(self, name):
        self.name_to_player(name).kill()
        self.names.pop(name)
    def name_to_player(self, name):
        if not name in self.names:
            return None
        for player in self:
            if player.name == name:
                return player

class ClientBlockClass():
    def __init__(self, name, location):
        self.name = name
        self.location = location