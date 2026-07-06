
import random
import math

from game_class.mm_class import Player
from game_class.game_class import Game
from game_class.sound_class import Sound

def damageResponse(self,amount,type):
    return 1

class iceSounds:
    BREAK1="ice_beam_break_1"
    BREAK2="ice_beam_break_2"
    BREAK3="ice_beam_break_3"
    BREAK4="ice_beam_break_4"
    BREAK5="ice_beam_break_5"
    BREAK6="ice_beam_break_6"
    BREAK7="ice_beam_break_7"
    BREAK8="ice_beam_break_8"
    BREAK9="ice_beam_break_9"
    BREAK10="ice_beam_break_10"
    BREAK11="ice_beam_break_11"
    def randomBreak(self):
        return random.choice([
            self.BREAK1,
            self.BREAK2,
            self.BREAK3,
            self.BREAK4,
            self.BREAK5,
            self.BREAK6,
            self.BREAK7,
            self.BREAK8,
            self.BREAK9,
            self.BREAK10,
            self.BREAK11,
        ])

def soundDict(game:Game):
    base=game.getRootPath()+"\\sound\\"
    return {
        iceSounds.BREAK1:base+"proj\\ice_beam\\ice_beam_break-01.wav",
        iceSounds.BREAK2:base+"proj\\ice_beam\\ice_beam_break-02.wav",
        iceSounds.BREAK3:base+"proj\\ice_beam\\ice_beam_break-03.wav",
        iceSounds.BREAK4:base+"proj\\ice_beam\\ice_beam_break-04.wav",
        iceSounds.BREAK5:base+"proj\\ice_beam\\ice_beam_break-05.wav",
        iceSounds.BREAK6:base+"proj\\ice_beam\\ice_beam_break-06.wav",
        iceSounds.BREAK7:base+"proj\\ice_beam\\ice_beam_break-07.wav",
        iceSounds.BREAK8:base+"proj\\ice_beam\\ice_beam_break-08.wav",
        iceSounds.BREAK9:base+"proj\\ice_beam\\ice_beam_break-09.wav",
        iceSounds.BREAK10:base+"proj\\ice_beam\\ice_beam_break-10.wav",
        iceSounds.BREAK11:base+"proj\\ice_beam\\ice_beam_break-11.wav"
    }

def AI(self,player:Player,game:Game,soundEng:Sound):
    TILESIZE=game.getTileSize()
    #spawn new
    if self.getCounter("spawn")==0:
        self.addCounter("spawn")
        self.setTimer("spawnNew",0.1)
    if self.getCounter("spawn")==1 and self.timerExpired("spawnNew"):
        self.addCounter("spawn")
        if "wall" not in self.state:
            if self.gethelpCount()==0:
                game.addProj(type(self)(self.getPos()[0]+(16 if self.facingLeft else -16),self.getPos()[1],16,5,facingLeft=self.facingLeft,Motion=self.Motion,Damage=self.getDamage(),ally=self.getAlly(),DType=self.getDamageType(),type="ice_beam",state="beam_mid_"+self.state.split("_")[-1],helpCount=self.gethelpCount()+1))
            elif self.gethelpCount()==1:
                game.addProj(type(self)(self.getPos()[0]+(16 if self.facingLeft else -16),self.getPos()[1],16,5,facingLeft=self.facingLeft,Motion=self.Motion,Damage=self.getDamage(),ally=self.getAlly(),DType=self.getDamageType(),type="ice_beam",state="beam_end_"+self.state.split("_")[-1],helpCount=self.gethelpCount()+1))
    
    if self.getSideBonk() and "hit" not in self.state:
        if self.facingLeft:
            newNum=math.floor(self.getPos()[0]%TILESIZE)
            if newNum<int(self.state.split("_")[-1]):
                self.state="beam_wall_"+str(newNum)
            else:
                self.state="beam_wall_0"
        else:
            newNum=math.floor(16-self.getPos()[0]%TILESIZE)
            if newNum<int(self.state.split("_")[-1]):
                self.state="beam_wall_"+str(newNum)
            else:
                self.state="beam_wall_0"
        
        oSize=self.getSize()
        pos=self.getPos()
        if int(self.state.split("_")[-1])<7:
            self.setSize([7,self.getSize()[1]],False)
        else:
            self.setSize([16-int(self.state.split("_")[-1]),self.getSize()[1]],False)
        self.setOffset([self.getOffset()[0],-5])
        self.toggleSideBonk()
        
    stateL=(self.state).split("_")
    if "wall" not in self.state:
        if self.timerExpired("turn"):
            self.setTimer("turn",0.0)
            if int(stateL[2])>7:
                stateL[2]="7"
            self.state=stateL[0]+"_"+stateL[1]+"_"+str((int(stateL[2])-1 if int(stateL[2])>0 else 7))
    else:
        newState=int(stateL[2])
        if newState==0:
            self.Motion=[0,0]
            self.state="beam_hitwall_0"
            self.setPos([self.getPos()[0]//TILESIZE*TILESIZE+(5 if self.facingLeft else 0),self.getPos()[1]])
            self.setSize([0,0],False)
            self.setOffset([0,-5])
            if self.getCounter("hitWall")==0 and self.timerExpired("hitWall"):
                self.addCounter("hitWall")
                self.setTimer("hitWall",5*(1+self.gethelpCount()))
                self.setPos([self.getPos()[0]+(0 if self.facingLeft else TILESIZE),self.getPos()[1]])
            elif self.getCounter("hitWall")==1 and self.timerExpired("hitWall"):
                from game_class.particle_class import Particle
                self.removeMe=True
                pos=self.getPos()
                for i in range(4):
                    game.addPart(Particle(pos[0]+random.randint(-8,8),pos[1]+random.randint(-8,8),3,3,f"flake_{random.randint(0,1)}",self.getAlly(),"snowflake",False,[0,0]))
                game.getSoundEng().play(iceSounds().randomBreak())
        else:
            self.state=stateL[0]+"_"+stateL[1]+"_"+str(newState)
            self.setSize([newState,self.getSize()[1]],False)
            if 7<newState:
                self.setOffset([(16-newState)*(1 if self.facingLeft else 0),-5])
            else:
                self.setOffset([(-7+newState)*(0 if self.facingLeft else 1)+(16-newState if self.facingLeft else 0),-5])