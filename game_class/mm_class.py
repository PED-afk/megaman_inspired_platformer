

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_class.game_class import Game
    from game_class.sound_class import Sound
from game_class.ent_class import Entity
from game_class.menu_class import Menu

import math
import time
import random
import pygame
from pygame.locals import *


from debug import writeLog, printLog


class playerSounds():
    TP="tp"
    BAR_FILL="barFill"
    BAR_DEP="barDep"
    SHOOT="playerShoot"
    LAND="playerLand"
    DIE="playerDie"
    RESPAWN="playerRespawn"




class Player(Entity):
    def __init__(self, game:Game, X = 0, Y = 0, W = 24, H = 24, state = "idle_0", ally = True, type = "", facingLeft:bool=False, Motion:list=None, maxMotion:list=None, speed:int=0.35, gravMult:int=1, dashSpeed:int=6, jumpForce:int=2.5):
        super().__init__(X, Y, W, H, state, ally, type, facingLeft, Motion, maxMotion, speed, gravMult, dashSpeed, jumpForce,HP=100,maxHP=100,invul=2)
        self.selectedW=0
        self.__lastW=0
        self.__maxEnergy=100

        #self.hasBalancer=False
        #self.hasCharge=False
        self.__equipment={
            "balancer":False,
            "charge":False
        }

        self.__weaponMenu=Menu("weaponMenu",[16,16],[16,"b"],[160,128],20,"royalblue3","mediumblue",4)

        self.__actions=[]

        #colors:
        #normal: "Color1":(0, 112, 236),"Color2":(0, 232, 216)
        #ice: "Color1":(211, 240, 241),"Color2":(63, 208, 212)
        #if im bored enough i use color pallets but I already made the player sprites so not now
        self.weapons={
            "Normal":{"E":-1,"name":"E. Blaster","D":1,"Cost":0,"speed":[5,0]},
            "Ice":{"E":100,"name":"Dry Ice Beam","D":1,"Cost":3,"speed":[4,0]},
            "Fire":{"E":100,"name":"Fire Edge","D":5,"Cost":4,"speed":[0,0]},
            "Elec":{"E":100,"name":"Elec. Shocker","D":1,"Cost":5,"speed":[0.2,0]},
            "Earth":{"E":100,"name":"Rock Rain","D":1,"Cost":10,"speed":[2,3]},
            "Water":{"E":100,"name":"Wave Maker","D":1,"Cost":3,"speed":[2.5,0]},
            "Metal":{"E":100,"name":"Metal Cycler","D":1,"Cost":2,"speed":[2,2]},
            "Light":{"E":100,"name":"Camera Flash","D":1,"Cost":10,"speed":[0,0]},
            "Dark":{"E":100,"name":"Shadow Dance","D":1,"Cost":5,"speed":[0,0]}
        }
        self.__infAmmo=False

        self.__binds={
            pygame.K_w:"up",
            pygame.K_s:"down",
            pygame.K_a:"left",
            pygame.K_d:"right",
            pygame.K_p:"pause",
            pygame.K_o:"fire",
            pygame.K_SPACE:"jump",
            pygame.K_LSHIFT:"dash",
            pygame.K_v:"weaponMenu",
            pygame.K_e:"nextW",
            pygame.K_q:"prevW",
            pygame.K_0:"directW0",
            pygame.K_1:"directW1",
            pygame.K_2:"directW2",
            pygame.K_3:"directW3",
            pygame.K_4:"directW4",
            pygame.K_5:"directW5",
            pygame.K_6:"directW6",
            pygame.K_7:"directW7",
            pygame.K_8:"directW8",
            pygame.K_9:"console"
        }
        self.__secretBinds={
            pygame.K_ESCAPE:"console"
        }
        #These can NOT (as in pls don't) and should NOT be changed during runtime
        #These will be used in situations where normal binds are diabled but the player
        #needs a way to escape the situation where normal binds are diabled

        self.__jumpACU=0.0

        self.__climbSpeed=1

        self.__consoleInputs=[]
    
    def getSounds(self,game:Game):
        base=game.getRootPath()+"\\sound\\"
        return {
            playerSounds.TP:base+"player\\MegamanWarp.wav",
            playerSounds.BAR_FILL:base+"player\\EnergyFill.wav",
            playerSounds.BAR_DEP:base+"player\\EnergyFill_R.wav",
            playerSounds.SHOOT:base+"player\\MegaBuster.wav",
            playerSounds.LAND:base+"player\\MegamanLand.wav",
            playerSounds.DIE:base+"player\\MegamanDefeat.wav",
            playerSounds.RESPAWN:base+"player\\MegamanDefeat_R.wav"
        }

    def update(self,game:Game):
        from game_class.particle_class import Particle
        from game_class.projectile_class import Projectile
        from game_class.enemy_class import Enemy

        def onRoomEdge():                    
            corners=self.getHitBoxCorners()
            corners=[corners[0],corners[2]]
            for cor in corners:
                X=math.floor(cor[0]/TILESIZE)
                Y=math.floor(cor[1]/TILESIZE)
                if X<1:
                    return {"dir":"left","player":math.floor(self.getPos()[1]/TILESIZE),"door":game.findDoor(side="left")}
                elif X>len(game.getCurRoomData()[0])-1:
                    return {"dir":"right","player":math.floor(self.getPos()[1]/TILESIZE),"door":game.findDoor(side="right")}
                elif Y<1:
                    return {"dir":"top","player":math.floor(self.getPos()[0]/TILESIZE),"door":game.findDoor(side="top")}
                elif Y>len(game.getCurRoomData())-1:
                    return {"dir":"bottom","player":math.floor(self.getPos()[0]/TILESIZE),"door":game.findDoor(side="bottom")}
            return None
        
        soundEng=game.getSoundEng()
        if self.getCounter("after1stTick")==0:
            self.addCounter("after1stTick")
            soundEng.set_volume(playerSounds.BAR_FILL,0.5)
            soundEng.set_volume(playerSounds.BAR_DEP,0.5)

        events=game.getDisplay().getEvents()

        if self.getCounter("addHealth")>0:
            game.setPaused(True)
            self.addCounter("addHealth",-1)
            if self.getHealth()<self.getMaxHealth():
                self.addHealth(1)
                soundEng.play(playerSounds.BAR_FILL,False)
            else:
                self.setCounter("addHealth",0)
            if self.getCounter("addHealth")==0:
                game.setPaused(False)
        elif self.getCounter("addHealth")<0:
            game.setPaused(True)
            self.addCounter("addHealth",1)
            if self.getHealth()>0:
                self.addHealth(-1)
                soundEng.play(playerSounds.BAR_DEP,False)
            else:
                self.setCounter("addHealth",0)
            if self.getCounter("addHealth")==0:
                game.setPaused(False)
        
        if self.getCounter("addAmmo")>0:
            game.setPaused(True)
            self.addCounter("addAmmo",-1)
            Wep=0
            if self.selectedW!=0 and self.getCurWEnergy()<self.__maxEnergy and self.getCurWEnergy()!=None:
                Wep=self.getCurWType()
            elif self.__equipment["balancer"]:
                Wep=self.__findLowestE()
            else:
                #"wasted" ammo; curent weapon can't be charged (base or already full)
                pass
            if Wep!=0:
                if self.weapons[Wep]["E"]<self.__maxEnergy:
                    self.weapons[Wep]["E"]+=1
                    soundEng.play(playerSounds.BAR_FILL,False)
                else:
                    self.setCounter("addAmmo",0)
            
            if self.getCounter("addAmmo")==0:
                game.setPaused(False)
        elif self.getCounter("addAmmo")<0:
            game.setPaused(True)
            self.addCounter("addAmmo",1)
            Wep=0
            if self.selectedW!=0 and self.getCurWEnergy()>0 and self.getCurWEnergy()!=None:
                Wep=self.getCurWType()
            elif self.__equipment["balancer"]:
                Wep=self.__findLowestE()
            else:
                #"wasted" ammo; curent weapon can't be charged (base or already full)
                pass
            if Wep!=0:
                if self.weapons[Wep]["E"]>0:
                    self.weapons[Wep]["E"]-=1
                    soundEng.play(playerSounds.BAR_DEP,False)
                else:
                    self.setCounter("addAmmo",0)
            
            if self.getCounter("addAmmo")==0:
                game.setPaused(False)
        
        if not self.timerExpired("invul"):
            self.setCounter("invul",1)
            interval=0.01
            if self.getTimer("invul")%interval<=interval/10:
                self.setTransparency(0.9 if self.getTransparency()==0.0 else 0.0)
        elif self.getCounter("invul")==1:
            self.resetCounter("invul")
            self.resetTransparency()

        TILESIZE=game.getTileSize()
        state=self.state
        if self.getBonk():
            self.toggleBonk()
            self.__jumpACU=99
        if self.getOnGround():
            self.__jumpACU=0.0
        notPaused= not game.getPaused()
        #collect inputs
        validConsoleKey={
            pygame.K_a:"a",
            pygame.K_b:"b",
            pygame.K_c:"c",
            pygame.K_d:"d",
            pygame.K_e:"e",
            pygame.K_f:"f",
            pygame.K_g:"g",
            pygame.K_h:"h",
            pygame.K_i:"i",
            pygame.K_j:"j",
            pygame.K_k:"k",
            pygame.K_l:"l",
            pygame.K_m:"m",
            pygame.K_n:"n",
            pygame.K_o:"o",
            pygame.K_p:"p",
            pygame.K_q:"q",
            pygame.K_r:"r",
            pygame.K_s:"s",
            pygame.K_t:"t",
            pygame.K_u:"u",
            pygame.K_v:"v",
            pygame.K_w:"w",
            pygame.K_x:"x",
            pygame.K_y:"y",
            pygame.K_z:"z",
            pygame.K_UNDERSCORE:"_",
            pygame.K_LSHIFT:"_",
            pygame.K_RSHIFT:"_",
            pygame.K_PERIOD:".",
            pygame.K_0:"0",
            pygame.K_1:"1",
            pygame.K_2:"2",
            pygame.K_3:"3",
            pygame.K_4:"4",
            pygame.K_5:"5",
            pygame.K_6:"6",
            pygame.K_7:"7",
            pygame.K_8:"8",
            pygame.K_9:"9",
            pygame.K_SPACE:" ",
            pygame.K_MINUS:"-",
            pygame.K_KP_MINUS:"-"

        }
        for e in events:
            if (e.type == KEYDOWN or e.type == KEYUP):
                if game.getConsole().getMenu().getActive() and e.type == KEYDOWN:
                    if e.key in self.__secretBinds:
                        action=self.__secretBinds[e.key]
                        if action not in self.__actions:
                            self.__actions.append(action)
                    if e.key==pygame.K_BACKSPACE:
                        self.__consoleInputs.append('\b')
                    elif e.key==pygame.K_RETURN:
                        self.__consoleInputs.append('\n')
                    elif e.key==pygame.K_DELETE:
                        self.__consoleInputs.append('\t')
                    elif e.key in validConsoleKey:
                        self.__consoleInputs.append(validConsoleKey[e.key])
                    else:
                        print("char cant be accepted; maybe when sound, play something")
                elif e.key in self.__binds:
                    action=self.__binds[e.key]
                    if e.type == KEYDOWN:
                        if action in ["pause","weaponMenu","nextW","prevW","console"]:
                            if action not in self.__actions:
                                self.__actions.append(action)
                        elif notPaused:
                            if action in self.__binds.values():
                                if action not in self.__actions:
                                    self.__actions.append(action)
                    elif e.type == KEYUP:
                        if action in self.__binds.values():
                            if action=="jump":
                                self.__jumpACU=99
                            if action in self.__actions:
                                self.__actions.remove(action)
        newActions=self.__actions

        #handle inputs
        for action in self.__actions:
            if action=="up":
                #stop up
                if not game.getTileSolid([self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1]+self.getSize()[1]/3*2])==2 and self.state=="climb_top_0":
                    if "idle" not in self.state:
                        self.state="idle_0"
                    self.setOnLadder(False)
                    self.setWasOnLadder(False)
                #at top
                if self.getOnLadder() and game.getTileSolid([self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1]+self.getSize()[1]])==2 and not game.getTileSolid([self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1]+self.getSize()[1]/2])==2:
                    if "top" not in self.state:
                        self.state="climb_top_0"
                #start climb
                if game.getTileSolid([self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1]+self.getSize()[1]/2])==2:
                    if "climb" not in self.state:
                        self.state="climb_0"
                    self.setOnLadder(True)
                    self.Motion=[0,0]
                    topCenter=self.getPos()[0]+self.getSize()[0]/2
                    newX=math.floor((topCenter)/TILESIZE)
                    self.setPos([newX*TILESIZE,self.getPos()[1]])
                #update pos
                if "climb" in self.state and "fire" not in self.state:
                    self.setPos([self.getPos()[0],self.getPos()[1]-self.__climbSpeed])
            elif action=="down":
                if "top" in self.state:
                    self.state="climb_0"
                #at bottom stop
                if not game.getTileSolid([self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1]+self.getSize()[1]+TILESIZE])==2 and "climb" in self.state:
                    self.state="idle_0"
                    self.setOnLadder(False)
                    self.setWasOnLadder(False)
                #start climb
                if (game.getTileSolid([self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1]+self.getSize()[1]/2])==2 and not self.getOnGround()) or (game.getTileSolid([self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1]+self.getSize()[1]+TILESIZE])==2 and self.getOnGround()):
                    if "climb" not in self.state:
                        self.state="climb_0"
                    self.setOnLadder(True)
                    self.Motion=[0,0]
                    topCenter=self.getPos()[0]+self.getSize()[0]/2
                    newX=math.floor(topCenter/TILESIZE)*TILESIZE
                    newY=self.getPos()[1]
                    if not game.getTileSolid([self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1]+self.getSize()[1]/2])==2:
                        newY=(math.floor(newY/TILESIZE)+2)*TILESIZE
                    self.setPos([newX,newY])
                #update pos
                if "climb" in self.state and "fire" not in self.state:
                    self.setPos([self.getPos()[0],self.getPos()[1]+self.__climbSpeed])
                    
            elif action=="left":
                if "dash" not in self.state:
                    if not self.getOnLadder():
                        self.Motion[0]-=self.getSpeed()
                        if "walk" not in state and self.getOnGround():
                            if "fire" not in state:
                                self.state="walk_0"
                            elif self.getCurWType()!=self.getCurWType(2):
                                self.state="walk_fire_1"
                    self.facingLeft=True
            elif action=="right":
                if "dash" not in self.state:
                    if not self.getOnLadder():
                        self.Motion[0]+=self.getSpeed()
                        if "walk" not in state and self.getOnGround():
                            if "fire" not in state:
                                self.state="walk_0"
                            elif self.getCurWType()!=self.getCurWType(2):
                                self.state="walk_fire_1"
                    self.facingLeft=False
            
            elif action=="pause":
                game.togglePaused()
                newActions.remove("pause")
            elif action=="fire":
                if self.getCurWEnergy()==-1 or self.getCurWEnergy()>=self.getCurWCost():
                    if self.timerExpired("fireCooldown"):
                        if ("fire" not in state and self.getCurWName()!=self.getCurWName(4)) or ("fire" not in state and self.getCurWName()==self.getCurWName(4) and not self.getOnGround() and not self.getOnLadder()):
                            if "idle" in state:
                                self.state="fire_0"
                            elif "walk" in state: # and self.getCurWName()!=self.getCurWName(2):
                                self.state="walk_fire_0"
                            elif "climb" in state:
                                self.state="climb_fire_0"
                            elif "jump" in state:
                                self.state="jump_fire_0"
                        if "fire" in state:
                            damage=self.getCurWDamage()
                            if self.getCurWName()==self.getCurWName(0):#normal
                                self.setTimer("fired",0.5)
                                self.setTimer("fireCooldown",0.1)
                                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="normal",type="lemon",state="idle_0"))
                                soundEng.play(playerSounds.SHOOT)
                            elif self.getCurWName()==self.getCurWName(1):#ice
                                self.setTimer("fired",0.5)
                                self.setTimer("fireCooldown",1.0)
                                self.removeAmmo(self.getCurWCost())
                                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,16,5,facingLeft=self.facingLeft,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="ice",type="ice_beam",state="beam_mid_0",helpCount=0))
                            elif self.getCurWName()==self.getCurWName(2):#fire
                                self.setTimer("fired",1)
                                if "walk" in state:
                                    self.state="fire_0"
                                if self.getCounter("fireAnim")==0:
                                    self.setTimer("nextAnim",0.1)
                                    self.setCounter("fireAnim",1)
                                    if "jump" in state:
                                        game.addProj(Projectile(self.getPos()[0]+(16 if self.facingLeft else -2),self.getPos()[1]-7,12,10,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="jump_fire_0",facingLeft=self.facingLeft))
                                        self.removeAmmo(self.getCurWCost())
                                    elif "climb" in state:
                                        game.addProj(Projectile(self.getPos()[0]+(5 if self.facingLeft else -7),self.getPos()[1]-8,21,10,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="climb_fire_0",facingLeft=self.facingLeft))
                                        self.removeAmmo(self.getCurWCost())
                                    else:
                                        game.addProj(Projectile(self.getPos()[0]+(13 if self.facingLeft else -3),self.getPos()[1]-3,14,18,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="fire_0",facingLeft=self.facingLeft))
                                        self.removeAmmo(self.getCurWCost())
                            elif self.getCurWName()==self.getCurWName(3):#elec
                                self.setTimer("fired",0.5)
                                self.setTimer("fireCooldown",2)
                                self.removeAmmo(self.getCurWCost())
                                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="elec",type="elec",state="idle_0"))
                            elif self.getCurWName()==self.getCurWName(4):#earth
                                self.setTimer("fired",4)
                                self.setWasOnLadder(False)
                                self.setOnLadder(False)
                                self.__jumpACU=99
                                if self.getCounter("fireAnim")==0:
                                    self.Motion=[0,self.getGravMult()*game.getGrav()*game.getGravMult()*-1]
                                    self.setTimer("nextAnim",0.5)
                                    self.setCounter("fireAnim",1)
                                    self.setSize([13,26])
                                    self.sizeChangeReason="earth_weapon"
                            elif self.getCurWName()==self.getCurWName(5):#water
                                self.setTimer("fired",0.5)
                                self.setTimer("fireCooldown",1)
                                self.removeAmmo(self.getCurWCost())
                                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="water",type="water",state="idle_0"))
                                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(1 if self.facingLeft else 0),self.getPos()[1]+self.getSize()[1]/3,Motion=[self.getCurWMotion()[0]*(1 if self.facingLeft else -1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="water",type="water",state="idle_0"))
                            elif self.getCurWName()==self.getCurWName(6):#metal
                                if "climb" in self.state or "jump" in self.state:
                                    self.setTimer("fireCooldown",1.75)
                                    self.setTimer("fired",0.5)
                                    self.removeAmmo(self.getCurWCost()*2)
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]*0.5],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),0],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]*-1*0.5],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                    
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(1 if self.facingLeft else 0),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(1 if self.facingLeft else -1),self.getCurWMotion()[1]*0.5],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(1 if self.facingLeft else 0),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(1 if self.facingLeft else -1),0],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(1 if self.facingLeft else 0),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(1 if self.facingLeft else -1),self.getCurWMotion()[1]*-1*0.5],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                elif "walk" in self.state:
                                    self.setTimer("fireCooldown",0.5)
                                    self.setTimer("fired",0.5)
                                    self.removeAmmo(self.getCurWCost())
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),0],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                else:
                                    self.setTimer("fireCooldown",2)
                                    self.setTimer("fired",5)
                                    self.removeAmmo(self.getCurWCost()*3)
                                    self.state="fire_0"
                                    self.setCounter("metal_fired",1)
                                    self.setTimer("metal_fired",0.1)
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1],6,6,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1)*0.5,self.getCurWMotion()[1]*-1],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1],6,6,Motion=[0,self.getCurWMotion()[1]*-1],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                                    game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]/2,self.getPos()[1],6,6,Motion=[self.getCurWMotion()[0]*(1 if self.facingLeft else -1)*0.5,self.getCurWMotion()[1]*-1],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                            elif self.getCurWName()==self.getCurWName(7):#light
                                self.setTimer("fired",0.5)
                                self.setTimer("fireCooldown",1.0)
                                self.removeAmmo(self.getCurWCost())
                                game.addProj(Projectile(self.getPos()[0],self.getPos()[1],0,0,facingLeft=self.facingLeft,Motion=[self.getCurWMotion()[0],self.getCurWMotion()[1]],Damage=damage,ally=True,DType="light",type="light",state="idle_0"))
                            elif self.getCurWName()==self.getCurWName(8):#dark
                                if game.getTileSolid([self.getPos()[0]+TILESIZE*(-1 if self.facingLeft else 1),self.getPos()[1]]) in [0,2]:
                                    self.setTimer("fired",0.5)
                                    self.setTimer("fireCooldown",1.0)
                                    damage=self.getCurWDamage(self.__lastW)/2
                                    game.addEnemy(Enemy(X=self.getPos()[0]+self.getSize()[0]*(-1 if self.facingLeft else 1),Y=self.getPos()[1]-1,W=24,H=24,state="idle_0",ally=True,type="shadow",facingLeft=self.facingLeft,Motion=[self.getCurWMotion()[0],self.getCurWMotion()[1]],maxMotion=None,speed=[0,0.2,6],damage=damage,contactDamage=damage))


            elif action=="jump":
                if (self.getOnGround() or (self.__jumpACU<10 and self.Motion[1]<0)) and not self.getOnLadder():
                    self.__jumpACU+=1
                    self.Motion[1]-=self.getJumpF()
                elif self.getOnLadder() and not {"up", "down"} & set(self.__actions): #ladder dismount
                    self.__jumpACU=99
                    self.state="jump_0"
                    self.setOnLadder(False)
            elif action=="weaponMenu":
                game.togglePaused()
                self.__weaponMenu.toggleActive()
                newActions.remove("weaponMenu")
            elif action=="nextW":
                if "fire" not in self.state:
                    self.__lastW=self.selectedW
                    curW=self.selectedW+1
                    if curW>len(self.weapons)-1:
                        curW=0
                    while self.getCurWEnergy(curW)==None:
                        curW+1
                        if curW>len(self.weapons)-1:
                            curW=0
                    self.selectedW=curW
                newActions.remove("nextW")
            elif action=="prevW":
                if "fire" not in self.state:
                    self.__lastW=self.selectedW
                    curW=self.selectedW-1
                    if curW<0:
                        curW=len(self.weapons)-1
                    while self.getCurWEnergy(curW)==None:
                        curW-1
                        if curW<0:
                            curW=len(self.weapons)-1
                    self.selectedW=curW
                newActions.remove("prevW")
            elif action=="dash":
                if self.getTimer("dash_end")==0:
                    self.setCounter("dash",0)
                newActions.remove("dash")
                if not self.getOnGround():
                    self.setCounter("dash",0)
                    continue
                if self.getCounter("dash")==0:
                    self.state="dash_0"
                    self.setTimer("dash_end",0.25)
                    self.setCounter("dash",1)
                    self.setTimer("dash_after",0.05)
            elif "direct" in action:
                dW=int(action[-1])
                if dW!=self.selectedW:
                    self.__lastW=self.selectedW
                    self.selectedW=dW
            elif action=="console":
                game.getConsole().toggleConsole()
                game.togglePaused()
                newActions.remove(action)
            else:
                writeLog("log",f"Unknown player action: {action}","player_class_action",True,False,"w","mm_class.py","update")
                printLog("error",f"Unknown player action: {action}","player_class_action")
        self.__actions=newActions

        if notPaused:
            if self.getHealth()>0:
                self.entUpdate(game,"player",self.__actions)
                roomEdge=onRoomEdge()
                if roomEdge:
                    if game.getCurRoom()["exit"][roomEdge["dir"]]["to"]!="pit":
                        game.changeCurRoom(roomEdge,self)
                    elif self.getPos()[1]>(len(game.getCurRoomData())+2)*TILESIZE:
                        self.dying("player",game)
                        self.setHealth(-1)
                        soundEng.play(playerSounds.DIE)
            else:
                if self.getHealth()!=-1:
                    self.setHealth(-1)
                    self.dying("player",game)
                    soundEng.play(playerSounds.DIE)

        self.__weaponMenu.tick(game)

        if game.getPaused():
            return

        #sprite update
        if self.getCurWName()==self.getCurWName(2):
            damage=self.getCurWDamage()
            if "climb" in state:
                if self.getCounter("fireAnim")==1 and self.timerExpired("nextAnim"):
                    self.state="climb_fire_1"
                    self.setTimer("nextAnim",0.05)
                    self.setCounter("fireAnim",2)
                    game.addProj(Projectile(self.getPos()[0]+(-5 if self.facingLeft else -0),self.getPos()[1]-13,21,26,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="climb_fire_1",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==2 and self.timerExpired("nextAnim"):
                    self.state="climb_fire_2"
                    self.setTimer("nextAnim",0.05)
                    self.setCounter("fireAnim",3)
                    game.addProj(Projectile(self.getPos()[0]+(-33 if self.facingLeft else +19),self.getPos()[1]-6,33,43,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="climb_fire_2",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==3 and self.timerExpired("nextAnim"):
                    self.state="climb_fire_3"
                    self.setTimer("nextAnim",0.1)
                    self.setCounter("fireAnim",4)
                    game.addProj(Projectile(self.getPos()[0]+(-29 if self.facingLeft else +18),self.getPos()[1]-6,29,39,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="climb_fire_3",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==4 and self.timerExpired("nextAnim"):
                    self.state="climb_0"
                    self.setCounter("fireAnim",0)
            elif "jump" in state:
                if self.getCounter("fireAnim")==1 and self.timerExpired("nextAnim"):
                    self.state="jump_fire_1"
                    self.setTimer("nextAnim",0.05)
                    self.setCounter("fireAnim",2)
                    game.addProj(Projectile(self.getPos()[0]+(-23 if self.facingLeft else 22),self.getPos()[1]-5,27,31,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="jump_fire_1",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==2 and self.timerExpired("nextAnim"):
                    self.state="jump_fire_2"
                    self.setTimer("nextAnim",0.05)
                    self.setCounter("fireAnim",3)
                    game.addProj(Projectile(self.getPos()[0]+(-29 if self.facingLeft else -5),self.getPos()[1]+1,60,43,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="jump_fire_2",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==3 and self.timerExpired("nextAnim"):
                    self.state="jump_fire_3"
                    self.setTimer("nextAnim",0.1)
                    self.setCounter("fireAnim",4)
                    game.addProj(Projectile(self.getPos()[0]+(10 if self.facingLeft else -6),self.getPos()[1]+20,22,24,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="jump_fire_3",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==4 and self.timerExpired("nextAnim"):
                    self.state="jump_fire_4"
                    self.setTimer("nextAnim",0.1)
                    self.setCounter("fireAnim",5)
                elif self.getCounter("fireAnim")==5 and self.timerExpired("nextAnim"):
                    self.state="jump_0"
                    self.setCounter("fireAnim",0)
            else:
                if self.getCounter("fireAnim")==1 and self.timerExpired("nextAnim"):
                    self.state="fire_1"
                    self.setTimer("nextAnim",0.05)
                    self.setCounter("fireAnim",2)
                    game.addProj(Projectile(self.getPos()[0]+(-11 if self.facingLeft else 7),self.getPos()[1]+5,30,19,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="fire_1",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==2 and self.timerExpired("nextAnim"):
                    self.state="fire_2"
                    self.setTimer("nextAnim",0.05)
                    self.setCounter("fireAnim",3)
                    game.addProj(Projectile(self.getPos()[0]+(-28 if self.facingLeft else -2),self.getPos()[1]-10,55,28,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="fire_2",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==3 and self.timerExpired("nextAnim"):
                    self.setTimer("nextAnim",0.1)
                    self.setCounter("fireAnim",4)
                    game.addProj(Projectile(self.getPos()[0]+(-24 if self.facingLeft else 0),self.getPos()[1]-10,48,29,Motion=self.getCurWMotion(),Damage=damage,ally=True,DType="fire",type="fire_sword",state="fire_3",facingLeft=self.facingLeft))
                elif self.getCounter("fireAnim")==4 and self.timerExpired("nextAnim"):
                    self.setTimer("nextAnim",0.1)
                    self.setCounter("fireAnim",5)
                elif self.getCounter("fireAnim")==5 and self.timerExpired("nextAnim"):
                    self.state="idle_0"
                    self.setCounter("fireAnim",0)
        elif self.getCurWName()==self.getCurWName(4):
            damage=self.getCurWDamage()
            if "fire" in self.state:
                self.Motion=[0,self.getGravMult()*game.getGravMult()*game.getGrav()*-1]
            if self.getCounter("fireAnim")==1 and self.timerExpired("nextAnim"):
                self.state="jump_fire_1"
                self.setSize([19,29])
                self.sizeChangeReason="earth_weapon"
                self.setTimer("nextAnim",0.75)
                self.setCounter("fireAnim",2)
            elif self.getCounter("fireAnim")==2 and self.timerExpired("nextAnim"):
                self.state="jump_fire_2"
                self.setSize([25,27])
                self.sizeChangeReason="earth_weapon"
                self.setTimer("nextAnim",1)
                self.setCounter("fireAnim",3)
                for i in range(5): #small
                    game.addProj(Projectile(self.getPos()[0]+random.randint(-15,10)*TILESIZE*(-1 if self.facingLeft else 1),self.getPos()[1]-(10+random.randint(0,4))*TILESIZE,8,8,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="earth",type="rock_fall",state=f"rock_3_{random.randint(0,3)}",facingLeft=False))
                for i in range(3): #mid1
                    game.addProj(Projectile(self.getPos()[0]+random.randint(-15,10)*TILESIZE*(-1 if self.facingLeft else 1),self.getPos()[1]-(10+random.randint(0,4))*TILESIZE,11,11,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="earth",type="rock_fall",state=f"rock_0_{random.randint(0,3)}",facingLeft=False))
                for i in range(2): #mid2
                    game.addProj(Projectile(self.getPos()[0]+random.randint(-15,10)*TILESIZE*(-1 if self.facingLeft else 1),self.getPos()[1]-(10+random.randint(0,4))*TILESIZE,13,13,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="earth",type="rock_fall",state=f"rock_1_{random.randint(0,3)}",facingLeft=False))
                for i in range(5): #large
                    game.addProj(Projectile(self.getPos()[0]+random.randint(-15,10)*TILESIZE*(-1 if self.facingLeft else 1),self.getPos()[1]-(10+random.randint(0,4))*TILESIZE,16,16,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]],Damage=damage,ally=True,DType="earth",type="rock_fall",state=f"rock_2_{random.randint(0,3)}",facingLeft=False))
                self.removeAmmo(self.getCurWCost())
            elif self.getCounter("fireAnim")==3 and self.timerExpired("nextAnim"):
                self.state="idle_0"
                self.resetSize()
                self.setCounter("fireAnim",0)
        elif self.getCurWName()==self.getCurWName(6) and self.getCounter("metal_fired")==1:
            damage=self.getCurWDamage()
            self.Motion=[0,0]
            if self.timerExpired("metal_fired"):
                self.state="fire_1"
                self.setTimer("fired",0.5)
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]*0.5],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),0],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(-1 if self.facingLeft else 1),self.getCurWMotion()[1]*-1*0.5],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(1 if self.facingLeft else 0),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(1 if self.facingLeft else -1),self.getCurWMotion()[1]*0.5],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(1 if self.facingLeft else 0),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(1 if self.facingLeft else -1),0],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(1 if self.facingLeft else 0),self.getPos()[1]+self.getSize()[1]/3,6,6,Motion=[self.getCurWMotion()[0]*(1 if self.facingLeft else -1),self.getCurWMotion()[1]*-1*0.5],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
                self.setCounter("metal_fired",0)

        if "dash" in state and self.getCounter("dash")==1:
            if self.getTimer("dash_end")==0:
                self.state="idle_0"
                self.setCounter("dash",0)
            else:
                if self.getSideBonk():
                    self.setCounter("dash",0)
                    self.toggleSideBonk()
                    self.state="idle_0"
                else:
                    self.Motion[0]=self.getDash()*(-1 if self.facingLeft else 1)
                    if self.getTimer("dash_after")==0:
                        pass
                    game.addPart(Particle(self.getPos()[0],self.getPos()[1],24,24,self.getCurWType().lower(),True,"p_dash",self.facingLeft))
                    self.setTimer("dash_after",0.05)

        if "jump" in state and self.getOnGround() and not (self.getCurWName()==self.getCurWName(4) and "fire" in state):
            self.state="idle_0"
            soundEng.play(playerSounds.LAND)
        elif "jump" not in state and not self.getOnGround() and "climb" not in state:
            self.state="jump_0"
            self.setCounter("dash",0)

        if not {"left", "right"} & set(self.__actions) and "walk" in state:
            self.state="idle_0"

        if self.getTimer("blink")==0 and (state=="idle_0" or state=="idle_1"):
            if state==f"idle_0":
                self.state=f"idle_1"
                self.setTimer("blink",0.1)
            else:
                self.state=f"idle_0"
                self.setTimer("blink",round(random.uniform(0.3,2),3))

        if self.timerExpired("fired") and "fire" in state:
            self.resetOffset()
            if "walk" in state:
                self.state="walk_1"
            elif "climb" in state:
                self.state="climb_0"
            elif "jump" in state:
                self.state="jump_0"
            else:
                self.state="idle_0"

        if self.getTimer("walkCycle")==0:
            if "walk" in state:
                extra=""
                for i in range(2):
                    for frame in range(0,5):
                        if state==f"walk_{extra}{frame}":
                            self.state=f"walk_{extra}{(frame if frame<4 else 0)+1}"
                    extra="fire_"
                self.setTimer("walkCycle",0.1)
            elif "climb" in state and "fire" not in state and {"up", "down"} & set(self.__actions):
                extra=""
                for i in range(2):
                    for frame in range(0,2):
                        if state==f"climb_{extra}{frame}":
                            self.state=f"climb_{extra}{(frame if frame==0 else -1)+1}"
                    extra="top_"
                self.setTimer("walkCycle",0.1)
    


    def getEquipment(self):
        return self.__equipment
    def setEquipment(self,what:str,towhat:bool=True):
        if what in self.__equipment:
            self.__equipment[what]=towhat

    def getInfAmmo(self):
        return self.__infAmmo
    def toggleInfAmmo(self):
        self.__infAmmo=(False if self.__infAmmo else True)

    def getWeaponMenu(self):
        return self.__weaponMenu
    
    def getConsoleInputs(self):
        returns=self.__consoleInputs
        self.__consoleInputs=[]
        return returns

    def getMaxEnergy(self):
        return self.__maxEnergy
    def setMaxEnergy(self,amount:int):
        self.__maxEnergy=amount

    def addAmmo(self, amount:int):
        self.setCounter("addAmmo",amount)
    def removeAmmo(self, amount:int, weaponID:int=None):
        if weaponID==None:
            weaponID=self.getCurWType()
        if self.getCurWEnergy()==-1:
            return
        self.weapons[weaponID]["E"]-=amount
        if self.weapons[weaponID]["E"]<0:
            self.weapons[weaponID]["E"]=0
    def setAmmo(self,amount:int,weaponID:int=None):
        if weaponID==None:
            weaponID=self.getCurWType()
        self.weapons[self.getCurWType(weaponID)]["E"]=amount

    def addPlayerHealth(self,amount:int):
        self.addCounter("addHealth",amount)


    def setBind(self,act:str,key:str):
        self.__binds.pop(list(self.__binds.keys())[list(self.__binds.values()).index(act)])
        self.__binds[key]=act


    def getCurWName(self,wIndex=None):
        """
        Returns the name (key) on index wIndex from self.weapons
        """
        if wIndex==None:
            wIndex=self.selectedW
        return self.weapons[list(self.weapons.keys())[wIndex]]["name"]
    def getCurWType(self,wIndex=None):
        if wIndex==None:
            wIndex=self.selectedW
        return list(self.weapons.keys())[wIndex]
    def getCurWEnergy(self,wIndex:int=None):
        """
        Returns the value of weapon on index wIndex from self.weapons
        """
        if wIndex==None:
            wIndex=self.selectedW
        return self.weapons[self.getCurWType(wIndex)]["E"]
    def getCurWDamage(self,wIndex:int=None):
        if wIndex==None:
            wIndex=self.selectedW
        return self.weapons[self.getCurWType(wIndex)]["D"]
    def getCurWCost(self,wIndex:int=None):
        if wIndex==None:
            wIndex=self.selectedW
        return self.weapons[self.getCurWType(wIndex)]["Cost"]
    def getCurWColor1(self,wIndex:int=None):
        if wIndex==None:
            wIndex=self.selectedW
        return self.weapons[self.getCurWType(wIndex)]["Color1"]
    def getCurWColor2(self,wIndex:int=None):
        if wIndex==None:
            wIndex=self.selectedW
        return self.weapons[self.getCurWType(wIndex)]["Color2"]
    def getCurWMotion(self,wIndex:int=None):
        if wIndex==None:
            wIndex=self.selectedW
        return self.weapons[self.getCurWType(wIndex)]["speed"]

    def setCurWDamage(self,wIndex:int=None,setTo:int=1):
        if wIndex==None:
            wIndex=self.selectedW
        self.weapons[self.getCurWType(wIndex)]["D"]=setTo

    def getLastWeapon(self):
        return self.__lastW

    def __findLowestE(self):
        """
        Returns the name of the weapon (key) with the lowest value in self.weapons
        """
        lowest=None
        lowestVal=math.inf
        for w in self.weapons:
            V=self.getCurWEnergy(list(self.weapons).index(w))
            if V!=None and V!=-1 and V<lowestVal:
                lowestVal=self.getCurWEnergy(list(self.weapons).index(w))
                lowest=w
        if lowest==list(self.weapons.keys())[0]:
            return None
        return lowest




