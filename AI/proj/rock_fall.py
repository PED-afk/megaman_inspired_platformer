
from game_class.mm_class import Player
from game_class.game_class import Game
from game_class.sound_class import Sound

def damageResponse(self,amount,type):
    return 1

def soundDict(game:Game):
    return {}

def AI(self,player:Player,game:Game,soundEng:Sound):
    if self.timerExpired("turn"):
        self.setTimer("turn",0.1)
        stateL=(self.state).split("_")
        self.state=stateL[0]+"_"+stateL[1]+"_"+str((int(stateL[2])+1 if int(stateL[2])<3 else 0))