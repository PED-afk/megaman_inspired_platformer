

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_class.sound_class import Sound


from game_class.ent_class import Entity
from game_class.mm_class import Player
from game_class.game_class import Game

from debug import writeLog, printLog

import random
import math

class Projectile(Entity):
    def __init__(self, X = 0, Y = 0, W = 8, H = 8, state = "idle_0", ally = True, type = "lemon", facingLeft:bool=False, Motion:list=None, maxMotion:list=None, speed:int=1, gravMult:int=1, dashSpeed:int=0, Damage:int=0, DType:str="normal",helpCount:int=0):
        super().__init__(X, Y, W, H, state, ally, type, facingLeft, Motion, maxMotion, speed, gravMult, dashSpeed, 0)
        """
        MaxMotion is not used; speed is never capped
        """
        self.__Damage=Damage
        self.__DamageType=DType
        self.__helpCount=helpCount

    def getDamage(self):
        return self.__Damage
    def getDamageType(self):
        return self.__DamageType

    def gethelpCount(self):
        return self.__helpCount
    
    def update(self,player:Player,game:Game,soundEng:Sound):
        self.entUpdate(game,"proj")
        if self.getDistanceTo(player)>30*game.getTileSize():
            self.removeMe=True
        if self.removeMe:
            return
        for ent in game.getEnemies()+[player]:
            if self.colliding(ent) and ent.getAlly()!=self.getAlly() and not ent.removeMe:
                from game_class.enemy_class import Enemy
                didNoDamage=1
                if isinstance(ent,Enemy):
                    didNoDamage=ent.damageMe(self.__Damage,self.__DamageType)
                else:
                    didNoDamage=ent.removeHealth(self.__Damage)
                if self.getType()=="elec" and "small" not in self.state:
                    didNoDamage=1
                if didNoDamage==0:
                    self.removeMe=True
        try:
            #not all projectiles have AIs because the default is to move in 1 direction, use 1 sprite and damage stuff
            #this is only for special projectiles that for example spawn new ones, change states, ect.
            game.getProjAI(self.getType())["AI"](self,player,game,soundEng)
        except KeyError:
            printLog("warning",f"Projectile '{self.getType()}' does not have an AI")
        except Exception as e:
            printLog("warning",f"Error in projectile AI '{self.getType()}': {e}")







