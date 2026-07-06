

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_class.sound_class import Sound


from game_class.ent_class import Entity
from game_class.game_class import Game
from game_class.mm_class import Player

from debug import printLog

import random

class Particle(Entity):
    def __init__(self, X = 0, Y = 0, W = 0, H = 0, state = "idle_0", ally = False, type = "", facingLeft = False, Motion = None, maxMotion = None, speed:int=0, gravMult:int=0, dashSpeed:int=0, jumpForce = 0):
        super().__init__(X, Y, W, H, state, ally, type, facingLeft, Motion, maxMotion, speed, gravMult, dashSpeed, jumpForce)
    
    def update(self,player:Player,game:Game,soundEng:Sound):
        self.entUpdate(game,"particle")
        self.updateTimers(game)
        try:
            #not all projectiles have AIs because the default is to move in 1 direction, use 1 sprite and damage stuff
            #this is only for special projectiles that for example spawn new ones, change states, ect.
            game.getPartAI(self.getType())["AI"](self,player,game,soundEng)
        except KeyError:
            printLog("warning",f"Projectile '{self.getType()}' does not have an AI")
        except Exception as e:
            printLog("warning",f"Error in projectile AI '{self.getType()}': {e}")




