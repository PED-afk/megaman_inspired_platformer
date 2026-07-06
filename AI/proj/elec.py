
import random
import math

from game_class.mm_class import Player
from game_class.game_class import Game
from game_class.sound_class import Sound

def damageResponse(self,amount,type):
    return 1

def soundDict(game:Game):
    return {}

def AI(self,player:Player,game:Game,soundEng:Sound):
    if self.timerExpired("pulse"):
        self.setTimer("pulse",0.01)
        stateL=(self.state).split("_")
        if stateL[0]=="small":
            if self.getCounter("spawn")==0:
                self.setTransparency(0.3)
                self.setCounter("spawn",1)
                self.setTimer("timeTillFade",1)
            if self.getCounter("startedFade")==0 and self.timerExpired("timeTillFade"):
                self.setCounter("startedFade",1)
                self.setTimer("fade",0.1)
            if self.getCounter("startedFade")==1:
                if self.timerExpired("fade"):
                    if self.getTransparency()!=1.0:
                        self.addTransparency(0.1)
                        self.setTimer("fade",0.1)
                    else:
                        self.removeMe=True
                        return
            stateSizes=[8,8,8]
            newState=(int(stateL[2])+1 if int(stateL[2])<2 else 0)
            newState=random.randint(0,2)
            self.state=stateL[0]+"_"+stateL[1]+"_"+str(newState)
            self.setSize([stateSizes[newState],stateSizes[newState]])
        else:
            self.setTransparency(0.1)
            stateSizes=[16,12,14]
            newState=(int(stateL[1])+1 if int(stateL[1])<2 else 0)
            newState=random.randint(0,2)
            self.state=stateL[0]+"_"+str(newState)
            self.setSize([stateSizes[newState],stateSizes[newState]])
            if self.timerExpired("spawn"):
                from game_class.projectile_class import Projectile
                self.setTimer("spawn",random.uniform(0.0,1.0))
                pos=self.getPos()
                size=self.getSize()
                speed=0.5
                for i in range(random.randint(1,4)):
                    yMult=random.randint(-2,2)
                    xMult=random.randint(-2,2)
                    while xMult==0 and yMult==0:
                        yMult=random.randint(-2,2)
                        xMult=random.randint(-2,2)
                    game.addProj(Projectile(pos[0]+size[0]/2-4,pos[1]+size[1]/2-4,8,8,"small_idle_0",self.getAlly(),"elec",False,[speed*xMult,speed*yMult],Damage=math.ceil(self.getDamage()/2),DType=self.getDamageType()))