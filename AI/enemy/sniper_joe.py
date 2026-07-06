

import random
import math

from game_class.mm_class import Player
from game_class.projectile_class import Projectile
from game_class.game_class import Game
from game_class.sound_class import Sound

if 0==1: #so editing this isnt suffering (code suggestions)
    from game_class.enemy_class import Enemy

#why
#not used
#idk why would this be needed
REPLACE=False


def damageResponse(self,amount,type):
    if self.state=="idle_0" or self.state=="jump_0":
        self.setTimer("cooldown",3)
        return 1
        
    if self.__weak!=None and type in self.__weak:
        self.removeHealth(amount*2)
    elif self.__weak!=None and type in self.__imune:
        self.removeHealth(math.floor(amount*0.5))
    else:
        self.removeHealth(amount)
    return 0

def soundDict(game:Game):
    return {}

def sniperJoeAI(self,player:Player,game:Game,soundEng:Sound):
    if 0==1: #so editing this isnt suffering (code suggestions)
        self=Enemy()

    if self.removeMe:
        return

    state=self.state
    if state=="jump_0" or state=="idle_0":
        if player.getPos()[0]<self.getPos()[0]:
            self.facingLeft=True
        else:
            self.facingLeft=False
    pos=self.getPos()
    if state=="idle_0":
        playerDist=self.getDistanceTo(player)
        if playerDist<4*game.getTileSize() and self.getPos()[1]>player.getPos()[1]+10:
            self.Motion[1]=-self.getJumpF()
            self.state="jump_0"
        elif playerDist<8*game.getTileSize() and self.getTimer("cooldown")==0:
            self.state="attack_0"
            self.setTimer("A",0.2)
    elif state=="attack_0":
        if self.getTimer("A")==0:
            self.state="attack_1"
            self.setTimer("timeBetweenShots",0.3)
            self.setCounter("shots",0)
    elif state=="attack_1":
        if self.getTimer("timeBetweenShots")==0 and self.getCounter("shots")<3:
            game.addProj(Projectile(pos[0],pos[1]+12,6,6,ally=False,type="sniper_joe",facingLeft=self.facingLeft,Motion=[2*(-1 if self.facingLeft else 1),0],speed=[0.1,0],Damage=self.getDamage()))
            self.setTimer("timeBetweenShots",0.5)
            self.addCounter("shots",1)
            if self.getCounter("shots")==3:
                self.setTimer("winddown",1.5)
        elif self.getCounter("shots")==3 and self.getTimer("winddown")==0:
            self.state="idle_0"
            self.setTimer("cooldown",random.uniform(4.0,6.0))
    elif state=="jump_0":
        if self.getOnGround():
            self.state="idle_0"