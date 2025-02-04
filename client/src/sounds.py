import pygame

class SoundEngineClass():
    def __init__(self, client):
        self.client = client
        self.enabled = True
        self.muted = False
        self.load_sounds()
    def load_sounds(self):
        sound_dir = "..\\data\\sounds\\"
        self.sounds = {"death": None, "myah": None, "pop": None}
        try:
            if self.client.player_name.lower() == 'bohunk':
                self.sounds["death"] = pygame.mixer.Sound(sound_dir + "joe_death.wav")
            else:
                self.sounds["death"] = pygame.mixer.Sound(sound_dir + "death.wav")
            self.sounds["myah"] = pygame.mixer.Sound(sound_dir + "myah.wav")
            self.sounds["pop"] = pygame.mixer.Sound(sound_dir + "pop.wav")
        except:
            self.client.log("Sounds could not be loaded!", "ERROR")
            self.mute()
        else:
            self.sounds["death"].set_volume(float(self.client.options["sound_volume"]))
            self.sounds["myah"].set_volume(1.)
    def play_sound(self, name):
        if self.enabled and not self.muted:
            try:
                self.sounds[name].play()
            except:
                self.client.log("Sound (" + name + ") could not be played!", "ERROR")
    def play_music(self, music = "PorkAnAngel"):
        if self.enabled and not self.muted:
            try:
                pygame.mixer.music.load("..\\data\\sounds\\" + music + ".ogg")
                pygame.mixer.music.set_volume(float(self.client.options["music_volume"]))
                pygame.mixer.music.play()
            except:
                self.client.log("Music (" + music + ") could not be played!", "ERROR")
    def stop_music(self):
        pygame.mixer.music.stop()
    def mute(self):
        self.muted = True
    def unmute(self):
        self.muted = False
    def toggle_mute(self):
        self.muted = not self.muted