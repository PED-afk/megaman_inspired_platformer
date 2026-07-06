


import random

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
    if self.getCounter("spawn")==0:
        self.addCounter("spawn")
        game.getSoundEng().set_volume(iceSounds.AMB,0.5)
        self.setTimer("playSound",random.uniform(0.0,0.6))
    if self.timerExpired("playSound") and self.getCounter("spawn")==1:
        self.addCounter("spawn")
        game.getSoundEng().play(iceSounds.AMB)
    
    if self.timerExpired("change"):
        stateL=(self.state).split("_")
        self.state=stateL[0]+"_"+str((int(stateL[1])+1 if int(stateL[1])<1 else 0))
        self.setTimer("change",random.uniform(0.1,1.0))
    speed=0.5
    dir=self.getCounter("dir")
    distance=self.getCounter("distance")
    distanceO=self.getCounter("distanceO")
    if dir==0:
        self.setCounter("dir",(-1 if random.randint(0,1)==0 else 1))
        r=random.randint(5*int(1/speed),16*int(1/speed))
        self.setCounter("distance",r)
        self.setCounter("distanceO",r)
    else:
        if distance<distanceO/8:
            self.Motion=[dir*speed,-speed/2]
        else:
            self.Motion=[dir*speed,speed/2]
        self.addCounter("distance",-1)
        if distance==0:
            self.setCounter("dir",0)



