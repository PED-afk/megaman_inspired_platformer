

import pygame

class Sound():
    def __init__(self, sound_files:dict, volume:float=1.0):
        """
        sound_files: dict {name:path}
        volume: 0.0 - 1.0
        """
        pygame.mixer.init()
        self.__sounds={}
        self.__volume=volume
        self.__playing=[]

        for name, path in sound_files.items():
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.__volume)
            self.__sounds[name]=sound

    def tick(self):
        self.__playing=[name for name in self.__playing if self.__sounds[name].get_num_channels()>0]

    def play(self, name:str, canMultInstance:bool=True):
        if name in self.__sounds:
            if canMultInstance:
                self.__sounds[name].play()
            else:
                if name not in self.__playing:
                    self.__playing.append(name)
                    self.__sounds[name].play()
        else:
            print(f"[SoundManager] Sound '{name}' not found.")

    def stop(self, name:str):
        if name in self.__sounds:
            self.__sounds[name].stop()
            if name in self.__playing:
                self.__playing.remove(name)

    def stop_all(self):
        pygame.mixer.stop()
        self.__playing=[]

    def set_volume(self, name:str, volume:float):
        self.__sounds[name].set_volume(max(0.0, min(1.0, volume)))

    def set_glob_volume(self, volume:float):
        #self.__sounds[name].get_volume()
        volume = max(0.0, min(1.0, volume))
        for sound in self.__sounds.values():
            sound.set_volume(sound.get_volume()/self.__volume*volume)
        self.__volume=volume

