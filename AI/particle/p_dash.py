

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
    if self.getTransparency()<1:
        if self.getTimer("Fade")==0:
            self.addTransparency(0.5/(self.getCounter("T")+1))
            if self.getTransparency()>1:
                self.setTransparency(1)
            self.addCounter("T",1)
            self.setTimer("Fade",0.1)
    else:
        self.removeMe=True