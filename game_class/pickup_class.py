

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_class.sound_class import Sound



from game_class.ent_class import Entity
from game_class.mm_class import Player
from game_class.game_class import Game


class Pickup(Entity):
    def __init__(self, X = 0, Y = 0, W = 0, H = 0, state = "idle_0", ally = False, type = "big_health", facingLeft:bool=False, Motion:list=None, maxMotion:list=None, speed:int=0, gravMult:int=1, dashSpeed:int=0, jumpForce:int=0, A:int=1):
        super().__init__(X, Y, W, H, state, ally, type, facingLeft, Motion, maxMotion, speed, gravMult, dashSpeed, jumpForce)
        self.__A=A
    
    def update(self,player:Player,game:Game,soundEng:Sound):
        if self.removeMe:
            return
        self.entUpdate(game,"pickup")

        self.facingLeft=False
        if self.getTimer("anim")==0:
            if self.state=="idle_0":
                self.state="idle_1"
            else:
                self.state="idle_0"
            self.setTimer("anim",0.1)
        if self.colliding(player):
            Amount=self.getA()
            if "ammo" in self.getType():
                if self.getAlly()!=player.getAlly():
                    Amount*=-1
                player.addAmmo(Amount)
            elif "health" in self.getType():
                if self.getAlly()!=player.getAlly():
                    Amount*=-1
                player.addPlayerHealth(Amount)
            self.removeMe=True
    
    def getA(self):
        return self.__A






