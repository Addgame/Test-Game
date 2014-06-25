import pygame
from colors import *

class GraphicsEngineClass():
    def __init__(self, client, screen, texture_directory = "default"):
        self.client = client
        self.texture_dir = texture_directory
        self.load_projectile_textures()
        self.load_hud_textures()
        self.load_block_textures()
        self.load_player_skins("_all")
        if screen != None:
            size = screen.get_size()
        else:
            size = [1366,768]
        self.create_display(size)
        self.client.clock.tick(float(self.client.options["fps"]))
    def create_display(self, size):
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("My Game v.0.0.4")
        pygame.display.set_icon(pygame.image.load("..\\data\\textures\\icon.png"))
        self.death_screen = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.death_screen.fill(REDFADE)
    def draw_screen(self):
        if self.client.game_state == "ingame":
            self.draw_game_screen()
    def draw_game_screen(self):
        self.draw_background()
        self.draw_blocks()
        self.draw_players()
        self.draw_projectiles()
        self.draw_messages()
        self.draw_hud()
        self.draw_cursor()
        pygame.display.update()
        self.client.clock.tick(float(self.client.options["fps"]))
    def draw_blocks(self):
        for block in self.client.blocks:
            self.screen.blit(self.block_textures[block["name"]], block["location"])
    def draw_players(self):
        for name in self.client.players:
            self.update_player_skins(name)
            if name != self.client.player_name:
                self.screen.blit(self.client.players[name]["current_img"], self.client.players[name]["location"])
        self.screen.blit(self.client.players[self.client.player_name]["current_img"], self.client.players[self.client.player_name]["location"])
    def draw_background(self):
        self.screen.fill(WHITE)
    def draw_messages(self):
        self.client.message_group.update()
        self.client.message_group.draw()
    def draw_cursor(self):
        self.client.cursor.draw()
    def draw_hud(self):
        location = [1, 1]
        hearts = self.client.players[self.client.player_name]["health"] / 20.0
        while hearts > 0:
            if hearts > .5:
                self.screen.blit(self.hud_textures["heart"], location)
                location[0] += self.hud_textures["heart"].get_width() + 1
            else:
                self.screen.blit(self.hud_textures["hearthalf"], location)
                location[0] += self.hud_textures["hearthalf"].get_width() + 1
            hearts -= 1
        if self.client.players[self.client.player_name]["movement"]["dead"] == True:
            self.screen.blit(self.death_screen, [0,0])
    def draw_projectiles(self):
        for identifier, data in self.client.projectiles.items():
            image = self.projectile_textures[data["type"]]
            if data["velocity"][0] < 0:
                image = pygame.transform.flip(image, True, False)
            self.screen.blit(image, data["location"])
    def load_player_skins(self, name):
        if name == "_all":
            for player_name in self.client.players:
                self.load_player_skins(player_name)
        else:
            if not self.client.players[name]["images"]:
                self.client.players[name]["images"] = {"player": pygame.image.load("..\\data\\textures\\players\\" + name + "\\player.png"), \
                    "playerCrouch": pygame.image.load("..\\data\\textures\\players\\" + name + "\\playerCrouch.png"), \
                    "playerCrouchJump": pygame.image.load("..\\data\\textures\\players\\" + name + "\\playerCrouchJump.png"), \
                    "playerDead": pygame.transform.rotate(pygame.image.load("..\\data\\textures\\players\\" + name + "\\player.png"), 90), \
                    "playerJump": pygame.image.load("..\\data\\textures\\players\\" + name + "\\playerJump.png")}
    def update_player_skins(self, name):
        img_name = "player"
        if self.client.players[name]["movement"]["crouch"] == True:
            img_name += "Crouch"
        if self.client.players[name]["movement"]["jump"] == True:
            img_name += "Jump"
        if self.client.players[name]["movement"]["dead"] == True:
            img_name += "Dead"
        self.client.players[name]["current_img"] = self.client.players[name]["images"][img_name]
    def load_block_textures(self):
        self.block_textures = {"dirt": None, "grass": None, "spike": None}
        for key in self.block_textures:
            try:
                self.block_textures[key] = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\blocks\\" + key + ".png")
            except:
                self.block_textures[key] = pygame.image.load("..\\data\\textures\\packs\\default\\blocks\\" + key + ".png")
    def get_cursor_textures(self):
        texture = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\cursor\\cursor.png")
        return texture
    def load_hud_textures(self):
        self.hud_textures = {"heart": None, "hearthalf": None}
        for key in self.hud_textures:
            try:
                self.hud_textures[key] = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\hud\\" + key + ".png")
            except:
                self.hud_textures[key] = pygame.image.load("..\\data\\textures\\packs\\default\\hud\\" + key + ".png")
    def load_projectile_textures(self):
        self.projectile_textures = {"missile": None}
        for key in self.projectile_textures:
            try:
                self.projectile_textures[key] = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\projectiles\\" + key + ".png")
            except:
                self.projectile_textures[key] = pygame.image.load("..\\data\\textures\\packs\\default\\projectiles\\" + key + ".png")