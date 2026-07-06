

import math


from game_class.mm_class import Player
from game_class.game_class import Game
from game_class.sound_class import Sound

from debug import printLog

def damageResponse(self,amount,type):
    return 1

def soundDict(game:Game):
    return {}

def AI(self,player:Player,game:Game,soundEng:Sound):
    print
    if self.getCounter("spawn")==0:
        self.setTimer("flash",0.5)
        self.addCounter("spawn")
    else:
        if self.timerExpired("flash"):
            if self.getCounter("flashC")==0:
                game.flash=True
                if game.getFlag("antiFlash"):
                    game.flashColor=(50,50,50)
                else:
                    game.flashColor=(200,200,200)
                self.setTimer("flash",0.01)
            elif self.getCounter("flashC")==1:
                game.flash=False
                self.setTimer("flash",0.05)
            elif self.getCounter("flashC")==2:
                game.flash=True
                game.damageEveryone(player,self.getDamage(),self.getDamageType(),self.getAlly())
                if game.getFlag("antiFlash"):
                    game.flashColor=(80,50,80)
                else:
                    game.flashColor=(230,200,230)
                self.setTimer("flash",0.01)
            elif self.getCounter("flashC")==3:
                game.flash=False
                self.removeMe=True
            self.addCounter("flashC")