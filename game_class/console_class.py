
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_class.game_class import Game

from game_class.menu_class import Menu
from helpers.sort import suggestuion_sort

from debug import printLog

class Console:
    def __init__(self,game:Game):
        self.__game=game
        self.__player=self.__game.getPlayer()
        self.__commands={
            "bind":"_bind #s #s",
            "disable_ai":"_disable_ai #s",
            "enable_ai":"_enable_ai #s",
            "set_grav_mult":"_set_grav_mult #f",
            "setflag":"_setflag #s #b",
            "hurtme":"_hurt #i",
            "set_energy_for_weapon":"_set_energy_for_weapon #s #i",
            "set_energy":"_set_energy #i",
            "set_hp":"_set_hp #i",
            "invul":"_toggle_god",
            "god":"_toggle_god",
            "inf_energy":"_toggle_inf_energy",
            "sv_cheats":"_toggle_cheats",
            "give_weapon":"_give_weapon #i",
            "take_weapon":"_take_weapon #i",
            "give_equpment":"_give_equpment #i",
            "take_equpment":"_take_equpment #i",
            "give_energy":"_give_energy #i",
            "give_hp":"_give_hp #i",
            "nuke":"_nuke",
            "my_nuke":"_nuke #i",
            "set_damage": "_set_damage #i",
            "set_max_hp":"_max_hp #i",
            "set_max_energy":"_max_energy #i",
            "impulse":"_impulse #i"
        }
        self.__cheater=False

        self.disabled_ais=[]
        self.__messages=[{"text":"test","color":(255,0,0)},{"text":"test2","color":(0,255,0)},{"text":"test3","color":(0,0,255)},{"text":"test","color":(255,0,0)},{"text":"test2","color":(0,255,0)},{"text":"test3","color":(0,0,255)},{"text":"test","color":(255,0,0)},{"text":"test2","color":(0,255,0)},{"text":"test3","color":(0,0,255)}]
        self.__messages=[]
        self.__incomplete=""

        self.__cursorBlinkTimer=0.0
        self.__cursor=False

        self.__menu=Menu("console",[0,0],[0,"t"],["sw",["sh",2/3]],10,"blueviolet","gray80",2)

        self.__conVars={}

    def getConVar(self,name:str):
        if name in self.__conVars:
            return self.__conVars[name]
        else:
            printLog("error",f"no conVar with name {name}",self.__conVars)
            printLog("info",f"creating conVar with name {name} and value 'None",self.__conVars)
            self.setConVar(name,None)
            return None
    
    def setConVar(self,name:str,value:any):
        self.__conVars[name]=value

    def __setTimer(self,time:float=0):
        self.__cursorBlinkTimer=time
    def __getTimer(self):
        return self.__cursorBlinkTimer
    def __updateTimer(self,game:Game):
        if self.__cursorBlinkTimer>0.0:
            self.__cursorBlinkTimer-=game.getMinFramTime()
            if game.deltaTime<0:
                self.__cursorBlinkTimer+=game.deltaTime
        if self.__cursorBlinkTimer<0.0:
            self.__cursorBlinkTimer=0.0
    def __timerExpired(self):
        return self.__cursorBlinkTimer==0
    

    def getMenu(self):
        return self.__menu

    def toggleConsole(self):
        self.__menu.toggleActive()

    def __addmessage(self,message:str,color:tuple=(255,255,255)):
        params={}
        params["color"]=color
        params["text"]=message
        self.__messages.append(params)

    def __evalCommand(self,command:str):
        self.__addmessage(command)
        comL=command.split(" ")
        mapping = {
            "True": True,
            "False": False,
            "None":None
        }
        args=[]
        if comL[0] in self.__commands:
            comFunc=self.__commands[comL[0]].split(" ")
            for i in range(1,len(comFunc)):
                try:
                    if comFunc[i]=="#s":
                        args.append(str(comL[i]))
                    elif comFunc[i]=="#i":
                        args.append(int(comL[i]))
                    if comFunc[i]=="#b":
                        args.append(mapping[comL[i]])
                    elif comFunc[i]=="#f":
                        args.append(float(comL[i]))
                except:
                    self.__addmessage("Wrong argument type!",(255,0,0))
            if len(self.__commands[comL[0]].split(" "))==len(comL):
                getattr(self,self.__commands[comL[0]].split(" ")[0])(*args)   
            else:
                self.__addmessage("Not enought arguments!",(255,0,0))
        elif comL[0] in self.__conVars:
            self.setConVar(comL[0],(int(comL[1]) if comL[1].isnumeric() else comL[1]))
            self.__addmessage(f"Set conVar {comL[0]} to value {comL[1]}")
        else:
            self.__addmessage(f"Unknown command: {comL[0]}",(255,0,0))

    def _bind(self,key:str,action:str):
        self.__player.setBind(action,key)
    def _disable_ai(self,ai_name:str):
        if ai_name not in self.disabled_ais:
            self.disabled_ais.append(ai_name)
    def _enable_ai(self,ai_name:str):
        if ai_name in self.disabled_ais:
            self.disabled_ais.remove(ai_name)
    def _set_grav_mult(self,m:int):
        self.__game.setGravMult(m)
    def _setflag(self,flag:str,newBool:bool):
        self.__game.setFlags(flag,newBool)

    def _hurt(self,damage:int):
        self.__player.addHealth(-damage)
    def _set_energy_for_weapon(self,weaponID:int,energy:int):
        self.__player.setAmmo(energy,weaponID)
    def _set_energy(self,energy:int):
        for i in range(1,8):
            self.__player.setAmmo(energy,i)
    def _set_hp(self,amount:int):
        self.__player.setHealth(amount)
    def _toggle_god(self):
        self.__player.toggleInvulFlag()
    def _toggle_inf_energy(self):
        self.__player.toggleInfAmmo()
    def _toggle_cheats(self):
        self.__cheater=(False if self.__cheater else True)
    def _give_weapon(self,weaponID:int):
        self.__player.setAmmo(self.__player.getMaxEnergy,weaponID)
    def _take_weapon(self,weaponID:int):
        self.__player.setAmmo(None,weaponID)
    def _give_equpment(self,equpment:str):
        self.__player.setEquipment(equpment,True)
    def _take_equpment(self,equpment:str):
        self.__player.setEquipment(equpment,False)
    def _give_energy(self,amount:int):
        from game_class.pickup_class import Pickup
        pos=self.__player.getPos()
        self.__game.addItem(Pickup(pos[0],pos[1]-3*self.__game.getTileSize(),16,12,"idle_0",True,"big_ammo",speed=[0,0.1],A=amount))
    def _give_hp(self,amount:int):
        from game_class.pickup_class import Pickup
        pos=self.__player.getPos()
        self.__game.addItem(Pickup(pos[0],pos[1]-3*self.__game.getTileSize(),16,16,"idle_0",True,"big_health",speed=[0,0.1],A=amount))
    def _nuke(self,amount:int=9999):
        self.__game.damageEveryone(self.__player,amount,"normal",self.__player.getAlly())
    def _set_damage(self,amount:int):
        self.__player.setCurWDamage(None,amount)
    def _max_hp(self,amount:int):
        self.__player.setMaxHealth(amount)
    def _max_energy(self,amount:int):
        self.__player.setMaxEnergy(amount)

    def _impulse(self,impulse:int):
        if impulse==101:
            self._hurt(-self.__player.getMaxHealth())
            self._set_energy(self.__player.getMaxEnergy())
            self._give_equpment("balancer")
            self._give_equpment("charge")
        else:
            self.__addmessage("Invalid impulse.",(50,255,255))






    def tick(self, game:Game, inputs:list):
        self.__menu.tick(game)
        self.__updateTimer(game)
        for iStr in inputs:
            if iStr=='\b':
                self.__incomplete=self.__incomplete[:-1]
            elif iStr=='\t':
                self.__incomplete=""
            else:
                self.__incomplete+=iStr
            if '\n' in self.__incomplete:
                if len(self.__incomplete.split('\n')[0])>0:
                    self.__evalCommand(self.__incomplete.split('\n')[0])
                self.__incomplete=""
        
    def getMessages(self):
        extra=("_" if self.__cursor else " ")
        if self.__timerExpired():
            self.__cursor=(False if self.__cursor else True)
            self.__setTimer(0.5)
        return self.__messages+[{"text":self.__incomplete+extra,"color":(255,255,255)}]
    
    def getSuggestions(self):
        return suggestuion_sort(self.__commands.keys(),self.__incomplete)