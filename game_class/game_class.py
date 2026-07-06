
import math
import os
import importlib
import inspect


import states


from game_class.console_class import Console
from game_class.display_class import Display
from game_class.mm_class import Player
from game_class.sound_class import Sound

from debug import writeLog, printLog



class Game():
    def __init__(self,rootPath:str,flags:dict={"showHitbox":False}):
        def load_ai_modules(folder_path: str) -> dict:
            loaded = {}
            for file_name in os.listdir(folder_path):
                if not file_name.endswith(".py"):
                    continue
                module_name = os.path.splitext(file_name)[0]
                file_path = os.path.join(folder_path, file_name)
                # Load module dynamically
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module_data = {}
                # Find the single function in the file
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj) and obj.__module__ == module.__name__:
                        if name=="soundDict":
                            module_data["sound"]=obj
                        elif "AI" in name:
                            module_data["AI"] = obj
                        elif "damageResponse"==name:
                            module_data["damageResponse"]=obj
                # Load ALL_CAPS variables
                for name, value in vars(module).items():
                    if name.isupper():
                        module_data[name] = value
                loaded[module_name] = module_data
            return loaded

        self.__rootPath=rootPath
        self.__tileSize=16
        self.__gameScale=2
        self.__gameScaleChange=True


        #load AIs here to avoid loading stuff multiple times
        self.__enemyAIs=load_ai_modules(self.__rootPath+"\\AI\\enemy")
        temp=load_ai_modules(self.__rootPath+"\\custom\\AI\\enemy")
        for ai in temp:
            if not ("CANTREPLACE" in self.__enemyAIs[ai] and self.__enemyAIs[ai]["CANTREPLACE"]):
                self.__enemyAIs[ai]=temp[ai]
        self.__projAIs=load_ai_modules(self.__rootPath+"\\AI\\proj")
        temp=load_ai_modules(self.__rootPath+"\\custom\\AI\\proj")
        for ai in temp:
            if not ("CANTREPLACE" in self.__projAIs[ai] and self.__projAIs[ai]["CANTREPLACE"]):
                self.__projAIs[ai]=temp[ai]
                
        self.__partAIs=load_ai_modules(self.__rootPath+"\\AI\\particle")
        temp=load_ai_modules(self.__rootPath+"\\custom\\AI\\particle")
        for ai in temp:
            if not ("CANTREPLACE" in self.__partAIs[ai] and self.__partAIs[ai]["CANTREPLACE"]):
                self.__partAIs[ai]=temp[ai]

        self.__player=Player(self,self.__tileSize*3,self.__tileSize*6)
        self.__display=Display(self)
        self.__console=Console(self)
        self.__soundEng=Sound(self.__createSoundDict(),1.0)

        self.__player.getWeaponMenu().toggleActive()
        self.__player.getWeaponMenu().toggleActive()
        self.__console.getMenu().toggleActive()
        self.__console.getMenu().toggleActive()
        self.__console.setConVar("developer",0)
        

        self.__running=True
        self.__isPaused=False
        self.__state=0
        self.__maxFPS=60
        self.__minFrameDur=1/self.__maxFPS
        self.frameStart=None
        self.frameEnd=None
        self.deltaTime=0
        self.__time=0

        self.hudPos=[50,30]
        self.__debugflags=flags

        self.__enemies=[]
        self.__items=[]
        self.__projs=[]
        self.__particles=[]
        self.__enCount=0
        self.__itCount=0
        self.__prCount=0
        self.__paCount=0

        self.flash=False
        self.flashColor=(0,0,0)

        self.__levels={}
        self.__currentLevel="level1"
        self.__currentRoom=""

        #self.cameraPos=[0,0]
        self.__borderedW=False
        if self.__borderedW:
            self.borderSize=[9,37]
        else:
            self.borderSize=[0,0]

        self.__darkness=0.0
        self.__fadeDir=0

        self.__glob_grav_mult=1.0
        self.__grav=0.2

        self.__gameVolume=1.0
        self.__soundEng.set_glob_volume(self.__gameVolume)

    def getEnemyAI(self,name:str):
        return self.__enemyAIs[name]
    def getProjAI(self,name:str):
        return self.__projAIs[name]
    def getPartAI(self,name:str):
        return self.__partAIs[name]

    def __createSoundDict(self):
        returnDict=self.__player.getSounds(self)
        for i in self.__enemyAIs.values():
            returnDict.update(i["sound"](self))
        for i in self.__projAIs.values():
            returnDict.update(i["sound"](self))
        for i in self.__partAIs.values():
            returnDict.update(i["sound"](self))
        return returnDict
    def getSoundEng(self):
        return self.__soundEng

    def getGravMult(self):
        return self.__glob_grav_mult
    def getGrav(self):
        return self.__grav
    def setGravMult(self,amount:int):
        self.__glob_grav_mult=amount
    def setGrav(self,amount:int):
        self.__grav=amount
    
    def getPlayer(self):
        return self.__player
    def getDisplay(self):
        return self.__display
    def getConsole(self):
        return self.__console
    
    def getRootPath(self):
        return self.__rootPath

    def damageEveryone(self,player,damage:int,damageType:str,ally:bool=True):
        for ent in self.getEnemies()+[player]:
            if ent.getAlly()!=ally:
                from game_class.enemy_class import Enemy
                if isinstance(ent,Enemy):
                    ent.damageMe(damage,damageType)
                else:
                    ent.removeHealth(damage)

    def cleanEnts(self):
        newEnts=[]
        c=0
        for ents in self.__enemies:
            if not ents.removeMe:
                newEnts.append(ents)
                c+=1
        self.__enemies=newEnts
        self.__enCount=c
        newEnts=[]
        c=0
        for ents in self.__items:
            if not ents.removeMe:
                newEnts.append(ents)
                c+=1
        self.__items=newEnts
        self.__itCount=c
        newEnts=[]
        c=0
        for ents in self.__projs:
            if not ents.removeMe:
                newEnts.append(ents)
                c+=1
        self.__projs=newEnts
        self.__prCount=c
        newEnts=[]
        c=0
        for ents in self.__particles:
            if not ents.removeMe:
                newEnts.append(ents)
                c+=1
        self.__particles=newEnts
        self.__paCount=c

    def getTileSize(self):
        return self.__tileSize

    def getTileSolid(self,pos:list):
        X=math.floor(pos[0]/(self.getTileSize()))
        Y=math.floor(pos[1]/(self.getTileSize()))
        try:
            return self.__levels[self.__currentLevel]["tiles"][str(self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]["data"][Y][X])]["solidType"]
        except IndexError:
            #print("error")
            return -1

    def getTilePath(self,pos:list):
        X=math.floor(pos[0]/(self.getTileSize()))
        Y=math.floor(pos[1]/(self.getTileSize()))
        try:
            return self.__levels[self.__currentLevel]["tiles"][str(self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]["data"][Y][X])]["path"]
        except IndexError:
            #print("error")
            return -1


    def getTilePathDirect(self,pos:list):
        try:
            return self.__levels[self.__currentLevel]["tiles"][str(self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]["data"][pos[1]][pos[0]])]["path"]
        except IndexError:
            #print("error")
            return -1

    def getCurLevel(self):
        return self.__levels[self.__currentLevel]
    
    def getCurRoomData(self):
        return self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]["data"]
    def getCurRoom(self):
        return self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]

    def getTileSolidDirect(self,pos:list):
        try:
            return self.__levels[self.__currentLevel]["tiles"][str(self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]["data"][pos[1]][pos[0]])]["solidType"]
        except IndexError:
            #print("error")
            return -1
    
    def findDoor(self,side):
        room=self.getCurRoomData()
        if side in ["left","right"]:
            for i in range(len(room)):
                if self.getTileSolidDirect([-1 if side=="right" else 0,i])==0:
                    return i
        else:
            if side=="top":
                room=room[0]
            else:
                room=room[-1]
            for i in range(len(room)):
                if self.getTileSolidDirect([i,0 if side=="top" else -1])==0:
                    return i
    
    def changeCurRoom(self,changeData:dict,player=None):
        from game_class.mm_class import Player
        if player!=None and not isinstance(player,Player):
            return
        try:
            if changeData==None or changeData["dir"]==None or changeData["door"]==None or changeData["player"]==None:
                return
        except:
            return
        
        dRoomState=self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]["exit"][changeData["dir"]]["changeNextBy"]
        nextRoom=self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]["exit"][changeData["dir"]]["to"]
        if nextRoom=="":
            nextRoom=self.__levels[self.__currentLevel]["startingRoom"]
        self.__currentRoom=nextRoom
        self.__levels[self.__currentLevel]["rooms"][self.__currentRoom]["roomstate"]+=dRoomState

        #set player pos:
        if player!=None:
            TILESIZE=self.getTileSize()
            SAFEDIS_CLOSE=2
            SAFEDIS_FAR=1
            if changeData["dir"]=="left":
                player.setPos([(len(self.getCurRoomData()[0])-SAFEDIS_CLOSE)*TILESIZE,(self.findDoor("right")+(changeData["player"]-changeData["door"]))*TILESIZE])
            elif changeData["dir"]=="right":
                player.setPos([SAFEDIS_FAR*TILESIZE,(self.findDoor("left")+(changeData["player"]-changeData["door"]))*TILESIZE])
                
            elif changeData["dir"]=="top":
                player.setPos([(self.findDoor("bottom")+(changeData["player"]-changeData["door"]))*TILESIZE,(len(self.getCurRoomData())-SAFEDIS_CLOSE)*TILESIZE])
            elif changeData["dir"]=="bottom":
                player.setPos([(self.findDoor("top")+(changeData["player"]-changeData["door"]))*TILESIZE,SAFEDIS_FAR*TILESIZE])


        self.flash=False
        
        self.__enemies=[]
        self.__items=[]
        self.__projs=[]
        self.__particles=[]

        for ent in self.getCurLevel()["rooms"][self.__currentRoom]["entityData"]:
            mapping = {
                "True": True,
                "False": False,
                "None": None
            }
            from game_class.enemy_class import Enemy
            from game_class.pickup_class import Pickup
            from game_class.projectile_class import Projectile
            from game_class.particle_class import Particle
            motionL=None
            if isinstance(ent["Motion"],list):
                motionL=[]
                for i in ent["Motion"]:
                    motionL.append(float(i))
            mMotionL=None
            if isinstance(ent["maxMotion"],list):
                mMotionL=[]
                for i in ent["maxMotion"]:
                    mMotionL.append(float(i))
            speedL=None
            if isinstance(ent["speed"],list):
                speedL=[]
                for i in ent["speed"]:
                    speedL.append(float(i))
            imuneL=None
            if isinstance(ent["imune"],list):
                imuneL=[]
                for i in ent["imune"]:
                    imuneL.append(i)
            weakL=None
            if isinstance(ent["weak"],list):
                weakL=[]
                for i in ent["weak"]:
                    weakL.append(i)
            
            if ent["eType"]=="enemy":
                #Enemy(X,Y,W,H,state,ally,type,face,motion,maxm,speed,jumpf,damage,contactDamage,hp,immune,weak,maxhp)
                self.addEnemy(Enemy(X=int(ent["X"]),Y=int(ent["Y"]),W=int(ent["W"]),H=int(ent["H"]),state=ent["state"],ally=mapping[ent["ally"]],type=ent["type"],facingLeft=mapping[ent["facingLeft"]],Motion=motionL,maxMotion=mMotionL,speed=speedL,jumpForce=float(ent["jumpForce"]),damage=int(ent["damage"]),contactDamage=int(ent["contactDamage"]),HP=int(ent["HP"]),imune=imuneL,weak=weakL))
            if ent["eType"]=="pickup":
                self.addItem(Pickup(X=int(ent["X"]),Y=int(ent["Y"]),W=int(ent["W"]),H=int(ent["H"]),state=ent["state"],ally=mapping[ent["ally"]],type=ent["type"],facingLeft=mapping[ent["facingLeft"]],Motion=motionL,maxMotion=mMotionL,speed=speedL,jumpForce=float(ent["jumpForce"]),A=int(ent["A"])))
            if ent["eType"]=="projectile":
                self.addProj(Projectile(int(ent["X"]),int(ent["Y"]),int(ent["W"]),int(ent["H"]),ent["state"],mapping[ent["ally"]],ent["type"],mapping[ent["facingLeft"]],motionL,mMotionL,speedL,int(ent["damage"]),ent["DamageType"]))
            if ent["eType"]=="particle":
                self.addPart(Particle(int(ent["X"]),int(ent["Y"]),int(ent["W"]),int(ent["H"]),ent["state"],mapping[ent["ally"]],ent["type"],mapping[ent["facingLeft"]],motionL,mMotionL,speedL,float(ent["jumpForce"]),int(ent["damage"]),int(ent["contactDamage"]),int(ent["HP"]),imuneL,weakL))

    def loadLevel(self,level:str):
        self.__currentLevel=level
        self.__currentRoom=self.__levels[self.__currentLevel]["startingRoom"]
        self.changeCurRoom({"dir":"self"})

    def addLevel(self,leveldata:dict):
        self.__levels[list(leveldata.keys())[0]]=leveldata[list(leveldata.keys())[0]]

    def getDark(self):
        return self.__darkness
    
    def setDarkDir(self,dir:int=0):
        if dir>=-1 or dir<=1:
            self.__fadeDir=dir

    def updateEveryone(self,player):
        if self.__enCount>20 or self.__itCount>20 or self.__prCount>20 or self.__paCount>20:
            self.cleanEnts()
        self.__darkness+=self.__fadeDir*self.deltaTime
        if self.__darkness<0.0:
            self.__darkness=0.0
        elif self.__darkness>1.0:
            self.__darkness=1.0
        from game_class.mm_class import Player
        if isinstance(player,Player):
            for enemy in self.__enemies:
                enemy.update(player,self,self.getSoundEng())
            for item in self.__items:
                item.update(player,self,self.getSoundEng())
            for p in self.__projs:
                p.update(player,self,self.getSoundEng())
            for p in self.__particles:
                p.update(player,self,self.getSoundEng())
    
    def update(self):
        player=self.__player
        self.getPlayer().update(self)
        if self.getPaused()==False:
            self.updateEveryone(player)
        self.getConsole().tick(self,player.getConsoleInputs())
        self.getDisplay().tick(self)
        self.getSoundEng().tick()

    def addEnemy(self,enemy):
        from game_class.enemy_class import Enemy
        if isinstance(enemy,Enemy):
            self.__enemies.append(enemy)
            self.__enCount+=1

    def addItem(self,item):
        from game_class.pickup_class import Pickup
        if isinstance(item,Pickup):
            self.__items.append(item)
            self.__itCount+=1

    def addProj(self,proj):
        from game_class.projectile_class import Projectile
        if isinstance(proj,Projectile):
            self.__projs.append(proj)
            self.__prCount+=1

    def addPart(self,particle):
        from game_class.particle_class import Particle
        if isinstance(particle,Particle):
            self.__particles.append(particle)
            self.__paCount+=1

    def getEnemies(self):
        return self.__enemies
    def getPickups(self):
        return self.__items
    def getProjectiles(self):
        return self.__projs
    def getParticles(self):
        return self.__particles



    def getMinFramTime(self):
        return self.__minFrameDur

    def getScale(self):
        return self.__gameScale
    def getScaleChange(self):
        return self.__gameScaleChange
    def okScaleChange(self):
        self.__gameScaleChange=False

    def setScale(self,newScale:int=2):
        if newScale!=self.getScale():
            self.__gameScale=newScale
            self.__gameScaleChange=True

    def getFlag(self,flag:str):
        if flag in self.__debugflags:
            return self.__debugflags[flag]
        return False
    
    def setFlags(self,flag:str, val:bool):
        self.__debugflags[flag]=val

    def generateCode(self):
        pass

    def getTime(self):
        return self.__time

    def __elapsed(self):
        self.deltaTime = self.frameEnd - self.frameStart
        self.__time+=self.deltaTime
        return self.deltaTime
    
    def sleepTime(self):
        return self.__minFrameDur - self.__elapsed()

    def getRun(self):
        return self.__running
    
    def setRun(self,new:bool):
        self.__running=new

    def getFPS(self):
        return self.__maxFPS
    
    def setFPS(self,FPS:int=60):
        if FPS>0:
            self.__maxFPS=FPS
            self.__minFrameDur=1/self.__maxFPS
            return 0
        return 1

    def getState(self):
        """
        returns value of __state
        """
        return self.__state
    
    def setState(self, newState:int):
        """
        Set __state to newState
        """
        self.__state=newState
        if newState==states.roomTrans:
            self.__isPaused=True
    
    def getPaused(self):
        """
        Returns value of __isPaused
        """
        return self.__isPaused
    def setPaused(self,isPaused:bool):
        """
        Sets __isPaused to param
        """
        self.__isPaused=isPaused
    def togglePaused(self):
        """
        Toggles __isPaused\nReturns new value
        """
        self.__isPaused=False if self.__isPaused else True
        return self.__isPaused



