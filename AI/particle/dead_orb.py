




import random
import math

from game_class.mm_class import Player
from game_class.game_class import Game
from game_class.sound_class import Sound

def damageResponse(self,amount,type):
    return 1

class iceSounds():
    AMB="snowflake_amb"

def soundDict(game:Game):
    base=game.getRootPath()+"\\sound\\"
    return {
        iceSounds.AMB:base+"proj\\ice_beam\\snow_amb.mp3",
    }

def AI(self,player:Player,game:Game,soundEng:Sound):
    pulseTimer=self.getTimer("pulse")
    sizes=[4,4,10,12,16,24]
    if pulseTimer==0:
        nextStateID=int(self.state[-1])+1
        if nextStateID>5:
            nextStateID=0
        self.state=f"idle_{nextStateID}"
        self.setSize([sizes[nextStateID],sizes[nextStateID]])
        self.setTimer("pulse",0.1)