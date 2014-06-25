import pygame

class SoundEngineClass():
    def __init__(self, client):
        self.client = client
        self.enabled = True
        self.load_sounds()
    def load_sounds(self):
        self.sounds = {"death": None}
        try:
            if self.client.player_name.lower() == 'bohunk':
                self.sounds["death"] = pygame.mixer.Sound("..\\data\\sounds\\joe_death.wav")
            else:
                self.sounds["death"] = pygame.mixer.Sound("..\\data\\sounds\\death.wav")
        except:
            self.client.log("Sounds could not be loaded!", "ERROR")
            self.mute()
        else:
            self.sounds["death"].set_volume(float(self.client.options["sound_volume"]))
    def play_music(self, music = "PorkAnAngel"):
        pygame.mixer.music.load("..\\data\\sounds\\" + music + ".ogg")
        pygame.mixer.music.set_volume(float(self.client.options["music_volume"]))
        pygame.mixer.music.play()
    def stop_music(self):
        pygame.mixer.music.stop()
    def mute(self):
        self.enabled = False 