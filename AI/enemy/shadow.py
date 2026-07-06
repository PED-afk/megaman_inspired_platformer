


from game_class.mm_class import Player
from game_class.projectile_class import Projectile
from game_class.game_class import Game
from game_class.sound_class import Sound

if 0==1: #so editing this isnt suffering (code suggestions)
    from game_class.enemy_class import Enemy

from debug import printLog


def damageResponse(self,amount,type):
    return 1

def soundDict(game:Game):
    return {}


def shadowAI(self,player:Player,game:Game,soundEng:Sound):
    if 0==1: #so editing this isnt suffering (code suggestions)
        self=Enemy()

    if self.getCounter("spawned")==0:
        self.addCounter("spawned")
        self.setTimer("startFade",5.0)
        lastW=player.getLastWeapon()
        if lastW in [1,3,5,6]:
            self.setCounter("weapon",lastW)
        else:
            self.setCounter("weapon",0)
        self.setDark(0.9)
        self.setTransparency(0.05)
    
    if self.timerExpired("startFade"):
        if self.getTransparency()!=1.0:
            self.addTransparency(0.01)
        else:
            self.removeMe=True
            return
    if not self.getOnGround():
        self.state="jump_0"
    else:
        if self.timerExpired("cooldown"):
            self.state="fire_0"
            pos=self.getPos()
            size=self.getSize()
            weapon=self.getCounter("weapon")
            
            
            damage=self.getDamage()
            wMotion=player.getCurWMotion(weapon if weapon!=8 else 0)
            if weapon==1:#ice
                self.setTimer("cooldown",1.0*2)
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,16,5,facingLeft=self.facingLeft,Motion=[wMotion[0]*(-1 if self.facingLeft else 1),wMotion[1]],Damage=damage,ally=True,DType="ice",type="ice_beam",state="beam_mid_0",helpCount=0))
            elif weapon==3:#elec
                self.setTimer("cooldown",2.0*2)
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,Motion=[wMotion[0]*(-1 if self.facingLeft else 1),wMotion[1]],Damage=damage,ally=True,DType="elec",type="elec",state="idle_0"))
            elif weapon==5:#water
                self.setTimer("cooldown",1.0*2)
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,Motion=[wMotion[0]*(-1 if self.facingLeft else 1),wMotion[1]],Damage=damage,ally=True,DType="water",type="water",state="idle_0"))
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(1 if self.facingLeft else 0),self.getPos()[1]+self.getSize()[1]/3,Motion=[wMotion[0]*(1 if self.facingLeft else -1),wMotion[1]],Damage=damage,ally=True,DType="water",type="water",state="idle_0"))
            elif weapon==6:#metal
                self.setTimer("cooldown",2.0*2)
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,Motion=[wMotion[0]*(-1 if self.facingLeft else 1),0],Damage=damage,ally=True,DType="metal",type="metal",state="idle_0"))
            else:#dark; normal; light; earth; fire
                self.setTimer("cooldown",0.1*2)
                game.addProj(Projectile(self.getPos()[0]+self.getSize()[0]*(0 if self.facingLeft else 1),self.getPos()[1]+self.getSize()[1]/3,Motion=[wMotion[0]*(-1 if self.facingLeft else 1),wMotion[1]],Damage=damage,ally=True,DType="normal",type="lemon",state="idle_0"))
            #this, I think, is bad practice but it works
            #addProj() uses append() and it always append to the end of the list so it's good here
            game.getProjectiles()[-1].setTransparency(self.getTransparency())