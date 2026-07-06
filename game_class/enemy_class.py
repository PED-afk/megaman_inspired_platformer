

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_class.sound_class import Sound

import math
import random

import os
import importlib.util
import inspect

from game_class.ent_class import Entity
from game_class.mm_class import Player
from game_class.game_class import Game

class Enemy(Entity):
    def __init__(self,X = 0, Y = 0, W = 0, H = 0, state = "idle_0", ally:bool = False, type:str="met", facingLeft:bool=False, Motion:list=None, maxMotion:list=None, speed:int=0, gravMult:int=1, dashSpeed:int=0, jumpForce:int=5, damage:int=1,contactDamage:int=1,HP:int=2,imune:list=None,weak:list=None,maxHP:int=5):
        super().__init__(X, Y, W, H, state, ally, type, facingLeft, Motion, maxMotion, speed, gravMult, dashSpeed, jumpForce,HP,maxHP)
        #weak and imune wont cause problems if empty (wont be used in ways that would crash if empty)
        self.__imune=imune
        self.__weak=weak
        self.__damage=damage
        self.__conDam=contactDamage
        """
        ROOT_PATH=os.path.dirname(os.path.abspath(__file__)).removesuffix("\\game_class")
        self.__AIs=load_ai_modules(ROOT_PATH+"\\AI")
        temp=load_ai_modules(ROOT_PATH+"\\custom\\AI")
        for ai in temp:
            if not ("CANTREPLACE" in self.__AIs[ai] and self.__AIs[ai]["CANTREPLACE"]):
                self.__AIs[ai]=temp[ai]
        """
    

    def update(self,player:Player,game:Game,soundEng:Sound):
        if self.removeMe:
            return
        self.entUpdate(game,"enemy")
        for ent in game.getEnemies()+[player]:
            if self.colliding(ent) and ent.getAlly()!=self.getAlly():
                player.removeHealth(self.__conDam)
        game.getEnemyAI(self.getType())["AI"](self,player,game,soundEng)


    def damageMe(self,amount:int,game:Game,type=None):
        if not self.timerExpired("invul"):
            return 1
        return game.getEnemyAI(self.getType())["damageResponse"](self,amount,type)

    def getDamage(self):
        return self.__damage


