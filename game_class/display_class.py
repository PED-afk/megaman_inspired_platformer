
from __future__ import annotations
from typing import TYPE_CHECKING

import pygame
from pygame.locals import *
import math
import os
import pyautogui

if TYPE_CHECKING:
    from game_class.mm_class import Player
    from game_class.game_class import Game

import states
from debug import writeLog, printLog


class Display:
    def __init__(self,game:Game):
        pygame.init()
        self.__game=game
        self.__rootPath=str(self.__game.getRootPath())
        
        self.__defWindowSize=[800,600]
        self.__curWindowSize=self.__defWindowSize

        self.__windowPos=[0,0]

        self.__screen=pygame.display.set_mode(self.__curWindowSize,flags=(pygame.NOFRAME | pygame.RESIZABLE),vsync=1)
        self.__Window = pyautogui.getActiveWindow()
        
        pcSSize=pygame.display.get_desktop_sizes()
        self.__screenSpace=[sum(i[0] for i in pcSSize),min(i[1] for i in pcSSize)]
        self.__sprites=self.__loadSprites(self.__rootPath+"\\sprite")
        self.__spriteCache=self.__sprites
        self.__pygameEvents=[]

        self.__distBetweenChar=2
        self.__distBetweenLine=2

    def getSize(self):
        return self.__curWindowSize
    def getDefSize(self):
        return self.__defWindowSize
    def resetSize(self):
        self.__curWindowSize=self.__defWindowSize
        return self.__curWindowSize
    def setSize(self,newSize:tuple):
        self.__curWindowSize=newSize

    def __editSprites(self,spritesDict,scale:int,prevKey:str=None):
        myDict={}
        for key, value in spritesDict.items():
            if isinstance(value, dict):
                myDict[key] = self.__editSprites(value,scale,key)
            elif isinstance(value, pygame.Surface):
                if prevKey=="characters":
                    myDict[key] = pygame.transform.scale(value,(value.get_width()*scale*0.5,value.get_height()*scale*0.5))
                else:
                    myDict[key] = pygame.transform.scale(value,(value.get_width()*scale,value.get_height()*scale))
            else:
                myDict[key] = value
        return myDict
    
    def __palette_swap(self,sprite, old_c, new_c):
        image = pygame.Surface((sprite.get_width(), sprite.get_height()))
        image.blit(sprite,(0,0))
        color_mask = pygame.mask.from_threshold(image, old_c, threshold=(1, 1, 1, 255))
        color_change_surf = color_mask.to_surface(setcolor=new_c, unsetcolor=(0, 0, 0, 0))
        img_copy = sprite.copy()
        img_copy.blit(color_change_surf, (0, 0))
        return img_copy
        
    def getEvents(self):
        return self.__pygameEvents

    def __loadSprites(self,path:str):
        images = {}
        errors=[]
        for root, dirs, files in os.walk(path):
            # Get relative path from base directory
            rel_path = os.path.relpath(root, path)    
            # Start at the root of the dict
            current_level = images
            # Build nested dict structure
            if rel_path != ".":
                for part in rel_path.split(os.sep):
                    current_level = current_level.setdefault(part, {})
            for file in files:
                if file.lower().endswith(".png"):
                    file_name = os.path.splitext(file)[0]
                    full_path = os.path.join(root, file)
                    try:
                        img = pygame.image.load(full_path).convert_alpha()
                        current_level[file_name] = img
                    except pygame.error as e:
                        errors.append(f"Failed to load {full_path}: {e}\n")
        if len(errors)>0:
            writeLog("error",errors,"spriteLoadFailed",True,False,"w","display_class","__loadSprites")
        return images

    def tick(self,game:Game):
        self.__pygameEvents=pygame.event.get()
        for e in self.__pygameEvents:
            if e.type == QUIT or (not game.getConsole().getMenu().getActive() and ((e.type == KEYDOWN and e.key == K_BACKSPACE) or (e.type == KEYDOWN and e.key == K_ESCAPE))):
                game.setRun(False)

        if game.getScaleChange():
            self.__spriteCache=self.__editSprites(self.__sprites,game.getScale())
            game.okScaleChange()

        self.__drawScreen(game)
        if game.getConsole().getMenu().getActive():
            pass #forgor why this here
        self.__drawConsole(game)
        pygame.display.update()
        self.__moveScreen(game)

    def __drawConsole(self,game:Game):
        scale=game.getScale()
        console=game.getConsole()
        menu=console.getMenu()
        consPos=menu.getPos()
        consSize=menu.getSize()
        edge=menu.getEdge()
        #larger
        pygame.draw.rect(self.__screen,menu.getColorEdge(),Rect((consPos[0]*scale,consPos[1]*scale),(consSize[0]*scale,consSize[1]*scale)),0)
        #smaller
        pygame.draw.rect(self.__screen,menu.getColorIn(),Rect([(consPos[0]+edge)*scale,consPos[1]*scale],((consSize[0]-edge*2)*scale,(consSize[1]-edge)*scale)),0)

        messages=console.getMessages()
        if len(messages)==0:
            return
        charSize=self.__sprites["UI"]["characters"]["a"].get_width()
        for i, message in enumerate(list(reversed(messages))):
            writeYpos=(consPos[1]+consSize[1]-edge)*scale-(1.5+(i)*1.5)*charSize*scale/2

            maxChar=(consSize[0]-edge*2)/((charSize+self.__distBetweenChar)*0.5)
            maxChar=int(maxChar)

            self.__writeHere([(edge+charSize*0.5)*scale+self.__windowPos[0],writeYpos+self.__windowPos[1]],message["text"][-maxChar:],game,(None if message["color"]==(252,252,252) else message["color"]))
            if writeYpos<0:
                break
        if len(messages[-1]["text"])<2:
            return
        suggestions=console.getSuggestions()
        for i, suggestion in enumerate(suggestions):
            writeYpos=(consPos[1]+consSize[1]-edge)*scale-(1.5+(i+1)*1.5)*charSize*scale/2

            maxChar=(consSize[0]-edge*2)/((charSize+self.__distBetweenChar)*0.5)
            maxChar=int(maxChar)

            self.__writeHere([(edge+charSize*0.5)*scale+self.__windowPos[0],writeYpos+self.__windowPos[1]],suggestion[-maxChar:],game,trans=0.5)
            if writeYpos<0:
                break

    def __writeHere(self,pos:list,this:str,game:Game,color:tuple=None,trans:int=0):
        scale=game.getScale()/2
        charSize=self.__sprites["UI"]["characters"]["a"].get_width()
        this=this.lower()
        transparency=int(255 * (1 - trans))
        replace={
            ",":"comma",
            ".":"dot",
            "?":"question",
            "!":"exclamation",
            "'":"apostropy",
            ">":"entry",
            ":":"colon",
            "/":"slash",
            "_":"underscore",
            "-":"dash"
        }
        newline=0
        space=0
        for idx,char in enumerate(this):
            if char=='\n':
                newline+=1
                continue
            if char==" ":
                space+=0.5
                continue
            if char=='\t':
                continue
            if char in replace:
                sprite=self.__spriteCache["UI"]["characters"][replace[char]]
            else:
                sprite=self.__spriteCache["UI"]["characters"][char]
            sprite.set_alpha(transparency)
            if color!=None:
                sprite=self.__palette_swap(sprite,(252,252,252),color)
            drawPos=[pos[0]-self.__windowPos[0]+(idx-space)*(charSize+self.__distBetweenChar)*scale,pos[1]-self.__windowPos[1]+newline*(charSize+self.__distBetweenLine)*scale]
            self.__screen.blit(sprite,(drawPos))
    
    def __drawScreen(self,game:Game):
        def drawActor(me,Iam:str):
            from game_class.mm_class import Player
            from game_class.particle_class import Particle

            def darken_sprite(sprite: pygame.Surface, amount: float) -> pygame.Surface:
                if amount==0.0:
                    return sprite
                amount=max(0.0, min(1.0, amount))
                result=sprite.copy()

                # Scale RGB channels only
                factor=int((1.0-amount)*255)
                result.fill((factor,factor,factor,255), special_flags=pygame.BLEND_RGBA_MULT)
                return result

            if me.removeMe:
                return
            myPos=me.getPos()
            myOffset=me.getOffset()

            #true pos
            myPos=[myPos[0]+myOffset[0],myPos[1]+myOffset[1]]
            
            mySize=me.getSize()

            if isinstance(me, Player):
                sprite=sprites[Iam][me.getCurWType().lower()][me.state]
                oSprite=self.__sprites[Iam][me.getCurWType().lower()][me.state]
                myPos[0]-=abs(oSprite.get_width()-mySize[0])//2
                #myPos[1]-=abs(oSprite.get_height()-mySize[1])//2
            elif isinstance(me, Particle):
                sprite=sprites[Iam][me.getType()][me.state]
            else:
                if me.getType()=="shadow":
                    sprite=sprites["player"][Player(game).getCurWType(me.getCounter("weapon")).lower()][me.state]
                else:
                    sprite=sprites[Iam][me.getType()][me.state]
            
            transparency=int(255 * (1 - me.getTransparency()))
            sprite.set_alpha(transparency)
            sprite=darken_sprite(sprite,me.getDark())
            if me.state not in ["climb_0", "climb_1", "climb_top_0", "climb_top_1"]:
                sprite=pygame.transform.flip(sprite,me.facingLeft,False)
            drawPos=[myPos[0]*scale-self.__windowPos[0],myPos[1]*scale-self.__windowPos[1]]
            self.__screen.blit(sprite,(drawPos))

        player=game.getPlayer()

        sprites=self.__spriteCache
        TILESIZE=game.getTileSize()

        state=game.getState()
        level=game.getCurLevel()
        room=game.getCurRoomData()
        scale=game.getScale()

        if state==states.title():
            self.__screen.fill((255,0,255))
        elif state==states.stageSelect():
            self.__screen.fill((255,100,255))
        elif state==states.levelLoad():
            self.__screen.fill((200,200,200))
        elif state==states.level():
            self.__screen.fill(tuple(level["defBGColor"]))
            bright=int(255 * (1 - game.getDark()))
            self.__screen.fill((bright, bright, bright), special_flags=pygame.BLEND_RGB_MULT)
            #draw map
            for rIdx, row in enumerate(room):
                for tIdx in range(len(row)):
                    sprite=sprites["tile"][game.getTilePathDirect([tIdx,rIdx])]
                    #sprite=pygame.transform.scale(sprite,(sprite.get_width()*scale,sprite.get_height()*scale))
                    bright=int(255 * (1 - game.getDark()))
                    sprite.fill((bright,bright,bright),special_flags=pygame.BLEND_RGB_MULT)
                    self.__screen.blit(sprite,((tIdx*TILESIZE)*scale-self.__windowPos[0],(rIdx*TILESIZE)*scale-self.__windowPos[1]))

            
            if game.getFlag("drawPlayer"):
                if player.getHealth()>0:
                    drawActor(player,"player")

            if game.getFlag("drawEnemy"):
                for enemy in game.getEnemies():
                    if enemy.getHealth()>0:
                        drawActor(enemy,"enemy")

            if game.getFlag("drawPickUp"):
                for item in game.getPickups():
                    if item.getHealth()>0:
                        drawActor(item,"pickup")

            if game.getFlag("drawProj"):
                for p in game.getProjectiles():
                    if p.getHealth()>0:
                        drawActor(p,"proj")

            if game.getFlag("drawPart"):
                for part in game.getParticles():
                    drawActor(part,"particle")

            if game.flash:
                pygame.draw.rect(self.__screen,game.flashColor,Rect([0,0],game.getDisplay().getSize()),0)

            if game.getFlag("drawHUD") and not game.getPlayer().getWeaponMenu().getActive():
                #32 bar aka 8*4 bar
                hudPos=game.hudPos
                percentMissing=1-player.getHealth()/player.getMaxHealth()
                blackBarNum=32*percentMissing
                for i in range(8):
                    if blackBarNum>=4:
                        sprite=sprites["hud"]["hp"]["0bar"]
                        blackBarNum-=4
                    elif blackBarNum>=3:
                        sprite=sprites["hud"]["hp"]["1bar"]
                        blackBarNum-=3
                    elif blackBarNum>=2:
                        sprite=sprites["hud"]["hp"]["2bar"]
                        blackBarNum-=2
                    elif blackBarNum>=1:
                        sprite=sprites["hud"]["hp"]["3bar"]
                        blackBarNum-=1
                    else:
                        sprite=sprites["hud"]["hp"]["4bar"]
                    self.__screen.blit(sprite,(hudPos[0],hudPos[1]+i*sprite.get_height()))

                if player.selectedW!=0:
                    percentMissing=1-player.getCurWEnergy()/player.getMaxEnergy()
                    blackBarNum=32*percentMissing
                    weapon=player.getCurWType().lower()
                    for i in range(8):
                        if blackBarNum>=4:
                            sprite=sprites["hud"]["weapon"][weapon]["0bar"]
                            blackBarNum-=4
                        elif blackBarNum>=3:
                            sprite=sprites["hud"]["weapon"][weapon]["1bar"]
                            blackBarNum-=3
                        elif blackBarNum>=2:
                            sprite=sprites["hud"]["weapon"][weapon]["2bar"]
                            blackBarNum-=2
                        elif blackBarNum>=1:
                            sprite=sprites["hud"]["weapon"][weapon]["3bar"]
                            blackBarNum-=1
                        else:
                            sprite=sprites["hud"]["weapon"][weapon]["4bar"]
                        self.__screen.blit(sprite,(hudPos[0]-sprite.get_width(),hudPos[1]+i*sprite.get_height()))

            if game.getPlayer().getWeaponMenu().getActive(): #weapon menu
                def getColor(value:int,maxValue:int):
                    percent=value/maxValue
                    if percent<0.1:
                        return (255,0,0)
                    elif percent<0.25:
                        return (255,165,0)
                    elif percent<0.50:
                        return (255,215,0)
                    else:
                        return None
                wMenu=game.getPlayer().getWeaponMenu()
                wMenuPos=wMenu.getPos()
                wMenuSize=wMenu.getSize()
                charSize=sprites["UI"]["characters"]["a"].get_width()
                edge=wMenu.getEdge()
                #larger
                pygame.draw.rect(self.__screen,wMenu.getColorEdge(),Rect([wMenuPos[0]*scale,wMenuPos[1]*scale],[wMenuSize[0]*scale,wMenuSize[1]*scale]),0)
                #smaller
                pygame.draw.rect(self.__screen,wMenu.getColorIn(),Rect([(wMenuPos[0]+edge)*scale,(wMenuPos[1]+edge)*scale],[(wMenuSize[0]-edge*2)*scale,(wMenuSize[1]-edge*2)*scale]),0)
                self.__writeHere([(wMenuPos[0]+edge)*scale+1*charSize+self.__windowPos[0],(wMenuPos[1]+edge)*scale+1*charSize+self.__windowPos[1]],(">" if player.selectedW==0 else "\t")+str(player.getCurWName(0))+": "+str(player.getHealth())+"/"+str(player.getMaxHealth()),game,getColor(player.getHealth(),player.getMaxHealth()))
                coulmn=0
                for i, w in enumerate(player.weapons):
                    if i==0:
                        continue
                    if player.getCurWEnergy(i)==None:
                        continue
                    if len(player.weapons)/2<=i:
                        coulmn=1
                        coulmn=0
                    self.__writeHere([(wMenuPos[0]+coulmn*(10*charSize)+edge)*scale+1*charSize+self.__windowPos[0],(wMenuPos[1]+edge)*scale+(1+i*1.5)*charSize+self.__windowPos[1]],(">" if player.selectedW==i else "\t")+str(player.getCurWName(i))+": "+str(player.getCurWEnergy(i))+"/"+str(player.getMaxEnergy()),game,getColor(player.getCurWEnergy(i),player.getMaxEnergy()))
            
            if game.getFlag("showHitbox"):
                if game.getFlag("drawPlayer"):
                    myPos=player.getPos()
                    mySize=player.getSize()
                    pygame.draw.rect(self.__screen,"blue",Rect([myPos[0]*scale-self.__windowPos[0],myPos[1]*scale-self.__windowPos[1]],[mySize[0]*scale,mySize[1]*scale]),1*scale)
                if game.getFlag("drawEnemy"):
                    for enemy in game.getEnemies():
                        myPos=enemy.getPos()
                        mySize=enemy.getSize()
                        pygame.draw.rect(self.__screen,"red",Rect([myPos[0]*scale-self.__windowPos[0],myPos[1]*scale-self.__windowPos[1]],[mySize[0]*scale,mySize[1]*scale]),1*scale)
                if game.getFlag("drawPickUp"):
                    for item in game.getPickups():
                        myPos=item.getPos()
                        mySize=item.getSize()
                        pygame.draw.rect(self.__screen,"yellow",Rect([myPos[0]*scale-self.__windowPos[0],myPos[1]*scale-self.__windowPos[1]],[mySize[0]*scale,mySize[1]*scale]),1*scale)
                if game.getFlag("drawProj"):
                    for p in game.getProjectiles():
                        myPos=p.getPos()
                        mySize=p.getSize()
                        pygame.draw.rect(self.__screen,"orange",Rect([myPos[0]*scale-self.__windowPos[0],myPos[1]*scale-self.__windowPos[1]],[mySize[0]*scale,mySize[1]*scale]),1*scale)
    
    def __moveScreen(self,game:Game):
        TILESIZE=game.getTileSize()
        screenMid=[self.__windowPos[0]+self.getSize()[0]/2,self.__windowPos[1]+self.getSize()[1]/2]
        playerPos=game.getPlayer().getPos()
        playerPos[0]*=game.getScale()
        playerPos[1]*=game.getScale()
        #X
        if playerPos[0]<screenMid[0]:
            self.__windowPos[0]+=playerPos[0]-screenMid[0]
            if self.__windowPos[0]<-1*game.borderSize[0]:
                self.__windowPos[0]=-1*game.borderSize[0]
        elif playerPos[0]>screenMid[0]:
            self.__windowPos[0]+=playerPos[0]-screenMid[0]
            if self.__windowPos[0]>((len(game.getCurRoomData()[0]))*TILESIZE*game.getScale())-self.getSize()[0]:
                self.__windowPos[0]=((len(game.getCurRoomData()[0]))*TILESIZE*game.getScale())-self.getSize()[0]
            if self.__windowPos[0]>self.__screenSpace[0]-self.getSize()[0]+game.borderSize[0]:
                self.__windowPos[0]=self.__screenSpace[0]-self.getSize()[0]
        #Y
        if playerPos[1]<screenMid[1]:
            self.__windowPos[1]+=playerPos[1]-screenMid[1]
            if self.__windowPos[1]<-1*game.borderSize[1]:
                self.__windowPos[1]=-1*game.borderSize[1]
        elif playerPos[1]>screenMid[1]:
            self.__windowPos[1]+=playerPos[1]-screenMid[1]
            if self.__windowPos[1]>((len(game.getCurRoomData()))*TILESIZE*game.getScale())-self.getSize()[1]:
                self.__windowPos[1]=((len(game.getCurRoomData()))*TILESIZE*game.getScale())-self.getSize()[1]
            if self.__windowPos[1]>self.__screenSpace[1]-self.getSize()[1]+game.borderSize[1]:
                self.__windowPos[1]=self.__screenSpace[1]-self.getSize()[1]

        self.__windowPos[0]=math.floor(self.__windowPos[0])
        self.__windowPos[1]=math.floor(self.__windowPos[1])

        winX=math.floor(self.__windowPos[0]-game.borderSize[0])
        self.__Window.moveTo(winX,math.floor(self.__windowPos[1]-game.borderSize[1]))
        
        #Scale screen
        YScale=math.floor(self.__screenSpace[1]/(len(game.getCurRoomData())*TILESIZE))
        XScale=math.floor(self.__screenSpace[0]/(len(game.getCurRoomData()[0])*TILESIZE))
        game.setScale(min(YScale,XScale))
        #screen cant be bigger than max level width/hight
        if len(game.getCurRoomData()[0])*TILESIZE*game.getScale()<self.getSize()[0]:
            self.setSize((len(game.getCurRoomData()[0])*TILESIZE*game.getScale(),self.getSize()[1]))
        if len(game.getCurRoomData())*TILESIZE*game.getScale()<self.getSize()[1]:
            self.setSize((self.getSize()[0],len(game.getCurRoomData())*TILESIZE*game.getScale()))

        #reserve ratio
        WSize=self.getSize()
        if WSize[0]>WSize[1]:
            self.setSize((round(self.getDefSize()[0]/self.getDefSize()[1]*WSize[1]),round(WSize[1])))
        else:
            self.setSize((round(WSize[0]),round(WSize[0]/(self.getDefSize()[0]/self.getDefSize()[1]))))


        self.__Window.resizeTo(self.getSize()[0],self.getSize()[1])




