
import random
import math

from game_class.mm_class import Player
from game_class.projectile_class import Projectile
from game_class.game_class import Game
from game_class.sound_class import Sound

if 0==1: #so editing this isnt suffering (code suggestions)
    from game_class.enemy_class import Enemy

def damageResponse(self,amount,type):
    if self.state=="idle_0":
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

def metAI(self,player:Player,game:Game,soundEng:Sound):
    if 0==1: #so editing this isnt suffering (code suggestions)
        self=Enemy()
    state=self.state
    if "idle" in state:
        if player.getPos()[0]<self.getPos()[0]:
            self.facingLeft=True
        else:
            self.facingLeft=False
    if state=="idle_0":
        if self.getDistanceTo(player)<6*game.getTileSize() and self.getTimer("cooldown")==0:
            self.state="attack_0"
            self.setSize([18,15])
            self.setPos([self.getPos()[0],self.getPos()[1]-2])
            self.setTimer("attacked",0.5)
    elif state=="attack_0" and self.getTimer("attacked")==0:
        pos=self.getPos()
        game.addProj(Projectile(pos[0],pos[1],6,6,ally=False,type="met",facingLeft=self.facingLeft,Motion=[2*(-1 if self.facingLeft else 1),0],speed=[0.1,0],Damage=self.getDamage()))
        game.addProj(Projectile(pos[0],pos[1],6,6,ally=False,type="met",facingLeft=self.facingLeft,Motion=[2*(-1 if self.facingLeft else 1),0.75],speed=[0.1,0],Damage=self.getDamage()))
        game.addProj(Projectile(pos[0],pos[1],6,6,ally=False,type="met",facingLeft=self.facingLeft,Motion=[2*(-1 if self.facingLeft else 1),-0.75],speed=[0.1,0],Damage=self.getDamage()))
        self.state="winddown_0"
        self.setTimer("winddown",1.0)
    elif state=="winddown_0" and self.getTimer("winddown")==0:
        self.state="idle_0"
        self.resetSize()
        self.setPos([self.getPos()[0],self.getPos()[1]+2])
        self.setTimer("cooldown",random.uniform(2.0,4.0))