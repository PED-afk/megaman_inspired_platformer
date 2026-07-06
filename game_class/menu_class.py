

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_class.game_class import Game

import math

from debug import writeLog



class Menu:
    def __init__(self,IDstr:str,onPos:int,offPos:int,size:list,speed:int,colorInner:str,colorEdge:str,edge:int):
        """
        assd
        """
        self.__IDstr=IDstr
        self.__size=size
        self.__curSize=None
        self.__onPos=onPos
        self.__offPos=offPos
        self.__animVal=[0,0]
        self.__curPos=[0,0]
        self.__speed=speed

        self.__isActive=False
        self.__apearing=False

        self.__colorInner=colorInner
        self.__colorEdge=colorEdge
        self.__edge=edge

    def getEdge(self):
        return self.__edge
    def getColorEdge(self):
        return self.__colorEdge
    def getColorIn(self):
        return self.__colorInner

    def getPos(self):
        return self.__curPos
    
    def getSize(self):
        return self.__curSize
    
    def getAnim(self):
        return self.__animVal
        
    def getActive(self):
        return self.__isActive
    def setActive(self,new:bool):
        #self.__isActive=new
        return
    def toggleActive(self):
        self.__isActive=True
        self.__apearing=(False if self.__apearing else True)
    
    def tick(self,game:Game):
        if self.__isActive:
            goal=self.__size.copy()

            replace={
                "sw":(game.getDisplay().getSize()[0]/game.getScale()),
                "sh":(game.getDisplay().getSize()[1]/game.getScale())
            }
            for i in range(2):
                if isinstance(goal[i],list):
                    if goal[i][0] in replace:
                        goal[i]=replace[goal[i][0]]*goal[i][1]
                    else:
                        goal[i]=goal[i][0]*goal[i][1]
                else:
                    if goal[i] in replace:
                        goal[i]=replace[goal[i]]
            self.__curSize=goal
            
            goal=(self.__onPos if self.__apearing else self.__offPos).copy()

            replace={
                "r":game.getDisplay().getSize()[0]/game.getScale(),
                "b":game.getDisplay().getSize()[1]/game.getScale(),
                "l":self.__curSize[0]*-1,
                "t":self.__curSize[1]*-1
            }
            if goal[0] in replace:
                goal[0]=replace[goal[0]]
            if goal[1] in replace:
                goal[1]=replace[goal[1]]

            done=0
            if self.__curPos[0]!=goal[0]:
                speed=self.__speed
                diff=self.__curPos[0]-goal[0]
                if abs(diff)<speed:
                    speed=diff
                self.__curPos[0]-=math.copysign(speed,diff)
            else:
                done+=1

            if self.__curPos[1]!=goal[1]:
                speed=self.__speed
                diff=self.__curPos[1]-goal[1]
                if abs(diff)<speed:
                    speed=diff
                self.__curPos[1]-=math.copysign(speed,diff)
            else:
                done+=1

            if done==2 and not self.__apearing:
                self.__isActive=False