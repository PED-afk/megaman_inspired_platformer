
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game_class.game_class import Game

import math


class Entity():
    def __init__(self,X:int=0,Y:int=0,W:int=0,H:int=0,state:str="idle0",ally:bool=False,type:str="", facingLeft:bool=False, Motion:list=None, maxMotion:list=None, speed:int=0, gravMult:int=1, dashSpeed:int=0, jumpForce:int=3,HP:int=5, maxHP:int=5, invul:int=0.5):
        self.__X=X
        self.__Y=Y
        self.__defW=W
        self.__defH=H
        self.__W=self.__defW
        self.__H=self.__defH
        self.sizeChangeReason=None
        
        self.__HP=HP
        if maxHP>=HP:
            self.__maxHP=maxHP
        else:self.__maxHP=HP
        
        self.__invulTimer=invul
        self.__invul=False

        self.state=state
        self.__ally=ally
        self.__type=type
    
        self.Motion = Motion if Motion is not None else [0,0]
        self.__maxMotion = maxMotion if maxMotion is not None else [2,2,5] #left/right, up, down
        #i will rewrite this at some day
        #i want to separate it into variables with talking names eg.: maxRunSpeed maxClimbSpeed etc.
        #capMotion uses it for sure idk what else

        self.__locGravMult=gravMult
        self.__speed=speed
        self.__dashSpeed=dashSpeed

        self.__timers={}
        self.facingLeft=facingLeft
        self.__offset=[0,0]
       
        self.__jumpForce= jumpForce

        self.__onGround=False
        self.__bonk=False
        self.__onLadder=False
        self.__wasOnLadder=False
        self.__sideBonk=False

        self.__transparency=0.0
        self.__darkness=0.0

        self.__counters={}

        self.removeMe=False

    def getDark(self):
        return self.__darkness
    def resetDark(self):
        self.__darkness=0.0
    def setDark(self,value:int):
        if 0.0<=value<=1.0:
            self.__darkness=value
    def addDark(self,value:int):
        if 0.0<=self.getDark()+value<=1.0:
            self.__darkness=value

    def resetOffset(self):
        self.__offset=[0,0]
    def getOffset(self):
        return self.__offset
    def setOffset(self,new:list):
        self.__offset=new

    def getCounter(self,name:str):
        if name not in self.__counters:
            self.__counters[name]=0
        return self.__counters[name]
    def setCounter(self,name:str,amount:int):
        self.__counters[name]=amount
    def addCounter(self,name:str,amount:int=1):
        if name in self.__counters:
            self.__counters[name]+=amount
        else:
            self.__counters[name]=amount
    def resetCounter(self,name:str):
        self.__counters[name]=0.0

    def addHealth(self,amount:int):
        self.__HP+=amount
        if self.__HP>self.__maxHP:
            self.__HP=self.__maxHP
    def getHealth(self):
        return self.__HP
    def setHealth(self,amount:int):
        if amount<=self.getMaxHealth():
            self.__HP=amount
    def removeHealth(self, amount:int):
        if amount<1:
            print("Tried to remove less than 1 HP")
            return 1
        if not self.timerExpired("invul"):
            return 1
        self.setTimer("invul",self.__invulTimer)
        self.__HP-=amount
        return 0
    
    def getInvulFlag(self):
        return self.__invul
    def toggleInvulFlag(self):
        self.__invul=(False if self.self.__invul else True)
    
    def getMaxHealth(self):
        return self.__maxHP
    def setMaxHealth(self,amount:int):
        self.__maxHP=amount

    def getTransparency(self):
        """
        Transparency between 0.0 and 1.0
        """
        return self.__transparency
    def addTransparency(self,value:float):
        """
        Transparency between 0.0 and 1.0
        """
        self.__transparency=max(0,min(self.getTransparency()+value,1.0))
    def setTransparency(self,new:float):
        """
        Transparency between 0.0 and 1.0
        """
        if 0.0<=new<=1.0:
            self.__transparency=new
    def resetTransparency(self):
        self.__transparency=0.0


    def setWasOnLadder(self,val:bool):
        self.__wasOnLadder=val
    def getWasOnLadder(self):
        return self.__wasOnLadder
    def setOnLadder(self,val:bool):
        self.__onLadder=val
    def getOnLadder(self):
        return self.__onLadder

    def getOnGround(self):
        return self.__onGround
    
    def getBonk(self):
        return self.__bonk
    def toggleBonk(self):
        self.__bonk=False if self.__bonk else True

    def getSideBonk(self):
        return self.__sideBonk
    def toggleSideBonk(self):
        self.__sideBonk=False if self.__sideBonk else True

    def entUpdate(self,game:Game,Iam:str,actions:list=None):
        def getCollPoints():
            pos=self.getPos()
            size=self.getSize()
            corners=self.getTerrainHBoxCorners(game)
            collisionOnPoints={
                "topLeft":game.getTileSolid(corners[0]),
                "top":game.getTileSolid([pos[0]+size[0]/2,pos[1]]),
                "topRight":game.getTileSolid(corners[1]),
                "right": game.getTileSolid([pos[0]+size[0],pos[1]+size[1]/2]),
                "bottomRight":game.getTileSolid(corners[2]),
                "bottom":game.getTileSolid([pos[0]+size[0]/2,pos[1]+size[1]]),
                "bottomLeft":game.getTileSolid(corners[3]),
                "left":game.getTileSolid([pos[0],pos[1]+size[1]/2])
            }
            return collisionOnPoints
        
        self.updateTimers(game)

        if self.getHealth()==0:
            self.removeMe=True
            return

        self.__sideBonk=False
        collisionOnPoints={}
        collisionOnPoints=getCollPoints()
        if Iam=="proj" or Iam=="particle":
            self.__X+=self.Motion[0]
            self.__Y+=self.Motion[1]
            if collisionOnPoints["left"]==1 or collisionOnPoints["right"]==1:
                self.__sideBonk=True
            return
        elif Iam=="player":
            if (2 in collisionOnPoints.values() and ("jump" in self.state and self.getWasOnLadder())) or self.getOnLadder():
                self.setSize([game.getTileSize()-1,29])
                self.sizeChangeReason="ladder"
            elif not self.getIsOriginalSize() and (self.sizeChangeReason==None or self.sizeChangeReason=="ladder"):
                #print(2 in collisionOnPoints.values(),("jump" in self.state and self.getWasOnLadder()))
                self.resetSize()
                self.setWasOnLadder(False)


        #left/right slowdown
        if actions!=None:
            if self.Motion[0]!=0 and not {"left", "right"} & set(actions):
                if abs(self.Motion[0])<abs(self.__speed/2):
                    self.Motion[0]=0
                else:
                    self.Motion[0]-=math.copysign(self.__speed/2,self.Motion[0])
        
        if self.getOnLadder():
            self.setWasOnLadder(True)
        collisionOnPoints=getCollPoints()
        if not collisionOnPoints["bottom"]==2 and not collisionOnPoints["top"]==2:
            self.setWasOnLadder(False)
        
        #gravity
        if "climb" not in self.state:
            self.Motion[1]+=self.__locGravMult*game.getGrav()*game.getGravMult()


        #collision
        self.__X+=self.Motion[0]
        collisionOnPoints=getCollPoints()
        if self.getOnLadder(): # on ladder
            #print("on ladder")
            self.__Y+=self.Motion[1]
            self.__onGround=False
            collisionOnPoints=getCollPoints()
            #down
            if collisionOnPoints["bottom"]==1:
                self.__onGround=True
                self.__onLadder=False
                while collisionOnPoints["bottom"]==1:
                    collisionOnPoints=getCollPoints()
                    self.__Y+=-0.1
                self.Motion[1]=0
            #up
            collisionOnPoints=getCollPoints()
            if collisionOnPoints["top"]==1:
                while collisionOnPoints["top"]==1:
                    collisionOnPoints=getCollPoints()
                    self.__Y+=0.1
                self.Motion[1]=0
        
        elif (collisionOnPoints["bottom"]==2 or collisionOnPoints["top"]==2) and self.getWasOnLadder(): # and not self.getOnGround()
            #print("falling at ladder")
            #left
            collisionOnPoints=getCollPoints()
            if collisionOnPoints["topLeft"]==1 or collisionOnPoints["bottomLeft"]==1 or collisionOnPoints["left"]==1:
                #print("left")
                while (collisionOnPoints["topLeft"]==1 or collisionOnPoints["bottomLeft"]==1 or collisionOnPoints["left"]==1):
                    self.__X-=math.copysign(0.1,self.Motion[0])
                    collisionOnPoints=getCollPoints()
                self.Motion[0]=0
            #right
            collisionOnPoints=getCollPoints()
            if collisionOnPoints["topRight"]==1 or collisionOnPoints["bottomRight"]==1 or collisionOnPoints["right"]==1:
                #print("right")
                while (collisionOnPoints["topRight"]==1 or collisionOnPoints["bottomRight"]==1 or collisionOnPoints["right"]==1):
                    self.__X-=math.copysign(0.1,self.Motion[0])
                    collisionOnPoints=getCollPoints()
                self.Motion[0]=0

            self.__Y+=self.Motion[1]
            self.__onGround=False
            collisionOnPoints=getCollPoints()
            #down
            if collisionOnPoints["bottom"]==1:
                self.__onGround=True
                self.__onLadder=False
                while collisionOnPoints["bottom"]==1:
                    collisionOnPoints=getCollPoints()
                    self.__Y+=-0.1
                self.Motion[1]=0
            #up
            collisionOnPoints=getCollPoints()
            if collisionOnPoints["top"]==1:
                while collisionOnPoints["top"]==1:
                    collisionOnPoints=getCollPoints()
                    self.__Y+=0.1
                self.Motion[1]=0

        else: #not on ladder
            #print("normal")
            #left
            collisionOnPoints=getCollPoints()
            if collisionOnPoints["topLeft"]==1 or collisionOnPoints["bottomLeft"]==1 or collisionOnPoints["left"]==1:
                if collisionOnPoints["left"]==1:
                    self.__sideBonk=True
                while (collisionOnPoints["topLeft"]==1 or collisionOnPoints["bottomLeft"]==1 or collisionOnPoints["left"]==1):
                    self.__X+=0.1
                    collisionOnPoints=getCollPoints()
                self.Motion[0]=0
            #right
            collisionOnPoints=getCollPoints()
            if collisionOnPoints["topRight"]==1 or collisionOnPoints["bottomRight"]==1 or collisionOnPoints["right"]==1:
                if collisionOnPoints["right"]==1:
                    self.__sideBonk=True
                while (collisionOnPoints["topRight"]==1 or collisionOnPoints["bottomRight"]==1 or collisionOnPoints["right"]==1):
                    self.__X-=0.1
                    collisionOnPoints=getCollPoints()
                self.Motion[0]=0

            self.__Y+=self.Motion[1]
            self.__onGround=False
            #down
            collisionOnPoints=getCollPoints()
            if collisionOnPoints["bottomLeft"]==1 or collisionOnPoints["bottomRight"]==1 or collisionOnPoints["bottom"]==1:
                #print("down")
                self.__onGround=True
                self.__onLadder=False
                while (collisionOnPoints["bottomLeft"]==1 or collisionOnPoints["bottomRight"]==1 or collisionOnPoints["bottom"]==1):
                    self.__Y-=0.1
                    collisionOnPoints=getCollPoints()
                self.Motion[1]=0
            #up
            collisionOnPoints=getCollPoints()
            if collisionOnPoints["topLeft"]==1 or collisionOnPoints["topRight"]==1 or collisionOnPoints["top"]==1:
                self.__bonk=True
                self.__Y-=self.Motion[1]
                self.Motion[1]=0

        collisionOnPoints=getCollPoints()
        if Iam=="player":
            if 3 in collisionOnPoints.values():
                self.setHealth(0)

        self.__capMotion()

    def dying(self,Iam:str,game:Game):
        from game_class.particle_class import Particle
        def spawnAllDeathPart(amount:int, speed:int=1):
            game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[speed,0],[10,10],[0,0],0))
            game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[0,speed],[10,10],[0,0],0))
            game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[-speed,0],[10,10],[0,0],0))
            game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[0,-speed],[10,10],[0,0],0))
            
            if amount==1:
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(45))*speed,math.sin(math.radians(45))*speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(45))*-speed,math.sin(math.radians(45))*speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(45))*-speed,math.sin(math.radians(45))*-speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(45))*speed,math.sin(math.radians(45))*-speed],[10,10],[0,0],0))
            elif amount==2:
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(30))*speed,math.sin(math.radians(30))*speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(30))*-speed,math.sin(math.radians(30))*speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(30))*-speed,math.sin(math.radians(30))*-speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(30))*speed,math.sin(math.radians(30))*-speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(60))*speed,math.sin(math.radians(60))*speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(60))*-speed,math.sin(math.radians(60))*speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(60))*-speed,math.sin(math.radians(60))*-speed],[10,10],[0,0],0))
                game.addPart(Particle(pPos[0],pPos[1],4,4,"idle_0",True,"dead_orb",False,[math.cos(math.radians(60))*speed,math.sin(math.radians(60))*-speed],[10,10],[0,0],0))
        
        self.updateTimers(game)
        pPos=self.getPos()
        pPos[0]+=self.getSize()[0]/2
        pPos[1]+=self.getSize()[1]/2
        if Iam=="player" or Iam=="boss":
            deathTimer=self.getTimer("dead")
            secondDeathTimer=self.getTimer("dead2")
            if secondDeathTimer==0 and deathTimer!=0:
                spawnAllDeathPart(0,0.9)
                self.setTimer("dead2",deathTimer*2)
            if deathTimer==0:
                self.setTimer("dead",10)
                self.setTimer("dead2",0.4)
                spawnAllDeathPart(1,1)
            elif deathTimer<=0.1:
                if Iam=="player":
                    game.setRun(False)

    def getJumpF(self):
        return self.__jumpForce
    
    def getSpeed(self):
        return self.__speed
    def getGravMult(self):
        return self.__locGravMult
    def getDash(self):
        return self.__dashSpeed
    
    def __capMotion(self):
        if abs(self.Motion[0])>self.__maxMotion[0]:
            self.Motion[0]=math.copysign(self.__maxMotion[0],self.Motion[0])
        if self.Motion[1]>0: #down
            if self.Motion[1]>self.__maxMotion[2]:
                self.Motion[1]=self.__maxMotion[2]
        elif self.Motion[1]<0:
            if self.Motion[1]<self.__maxMotion[1]*-1:
                self.Motion[1]=self.__maxMotion[1]*-1

    def getType(self):
        return self.__type
    
    def getAlly(self):
        return self.__ally

    def getPos(self):
        """
        Top left corner
        """
        return [self.__X,self.__Y]
    
    def setPos(self,newPos:list):
        self.__X,self.__Y=newPos
    
    def getSize(self):
        return [self.__W,self.__H]
    def getOriginalSize(self):
        return [self.__defW,self.__defH]
    def getIsOriginalSize(self):
        return self.getSize()==self.getOriginalSize()
    def resetSize(self,relocate:bool=True):
        if self.getIsOriginalSize():
            return self.getSize()
        pos=self.getPos()
        startSize=self.getSize()
        defSize=self.getOriginalSize()
        if relocate:
            self.setPos([pos[0]+(startSize[0]-defSize[0])/2,pos[1]+(startSize[1]-defSize[1])/2])
        self.__W=self.__defW
        self.__H=self.__defH
        self.sizeChangeReason=None
        return self.getSize()
    def setSize(self,newSize:list,relocate:bool=True):
        size=self.getSize()
        if newSize==size:
            return
        self.__W=newSize[0]
        self.__H=newSize[1]
        if relocate:
            pos=self.getPos()
            self.setPos([pos[0]+(size[0]-self.__W)/2,pos[1]+(size[1]-self.__H)/2])

    def setTimer(self,timerName:str,time:float=0):
        self.__timers[timerName]=time
    def addTimer(self,timerName:str,time:float):
        if timerName not in self.__timers:
            self.__timers[timerName]=0
        self.__timers[timerName]+=time
    def getTimer(self,timerName:str):
        if timerName in self.__timers:
            return self.__timers[timerName]
        self.__timers[timerName]=0
        return 0
    def updateTimers(self,game:Game):
        for timer in self.__timers:
            if self.__timers[timer]>0:
                self.__timers[timer]-=game.getMinFramTime()
                if game.deltaTime<0:
                    self.__timers[timer]+=game.deltaTime
            if self.__timers[timer]<0:
                self.__timers[timer]=0
    def timerExpired(self,timerName:str):
        return self.getTimer(timerName)==0
    def resetTimer(self,timerName:str):
        self.__timers[timerName]=0.0

    def getTerrainHBoxCorners(self,game:Game):
        points=[]
        W=self.getSize()[0]
        H=self.getSize()[1]
        points.append(self.getPos())
        points.append([self.__X+W,self.__Y])
        points.append([self.__X+W,self.__Y+H])
        points.append([self.__X,self.__Y+H])
        return points

    def getHitBoxCorners(self):
        points=[]
        points.append(self.getPos())
        points.append([self.__X+self.__W,self.__Y])
        points.append([self.__X+self.__W,self.__Y+self.__H])
        points.append([self.__X,self.__Y+self.__H])
        return points

    def colliding(self, other:"Entity"):
        myPoints=self.getHitBoxCorners()
        otherPoints=other.getHitBoxCorners()
        # If one rectangle is to the left of the other
        if myPoints[0][0]>otherPoints[1][0] or otherPoints[0][0]>myPoints[1][0]:#if l1.x > r2.x or l2.x > r1.x:
            return False
        # If one rectangle is above the other
        if myPoints[0][1]>otherPoints[2][1] or otherPoints[0][1]>myPoints[2][1]:#if r1.y > l2.y or r2.y > l1.y:
            return False

        return True
    
    def getDistanceTo(self, other:"Entity"):
        otherPos=other.getPos()
        return math.sqrt(((self.__X-otherPos[0])**2)+((self.__Y-otherPos[1])**2))

    def wantToGoThisWay(self,angle:int,speed:int):
        self.Motion=[math.cos(math.radians(angle))*speed,math.sin(math.radians(angle))*speed]
