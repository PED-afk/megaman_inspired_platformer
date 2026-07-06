
from game_class.mm_class import Player
from game_class.game_class import Game
from game_class.sound_class import Sound

def damageResponse(self,amount,type):
    return 1

def soundDict(game:Game):
    return {}

def AI(self,player:Player,game:Game,soundEng:Sound):
    if self.getTransparency()<1.0:
        self.addTransparency(0.1)
    else:
        self.removeMe=True