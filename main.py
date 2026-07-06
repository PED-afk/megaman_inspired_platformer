import pygame
from pygame.locals import *
import os
import time
import math
import pyautogui
import ctypes


from pathlib import Path
import traceback


from game_class.game_class import Game

import states

from load import load_json
from debug import writeLog, setupFolders, printLog



def main():
    setupFolders()

    def loadlevels(path:str):
        file_paths=[]
        file_names=[]
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                file_names.append(file)
                file_paths.append(full_path)

        file_count = len(file_paths)
        return file_paths, file_names, file_count



    ROOT_PATH=os.path.dirname(os.path.abspath(__file__))



    flags={"showHitbox":False,"drawPlayer":True,"drawEnemy":True,"drawProj":True,"drawPickUp":True,"drawHUD":True,"drawPart":True,"showOkMessages":True}
    try:
        flags=load_json(ROOT_PATH+"\\flags.json")
        interpret={"True":True,"False":False}
        for i in flags:
            flags[i]=interpret[flags[i]]
    except Exception as e:
        writeLog("error",traceback.format_exc(),"flag_load_error",True,False,"w","main.py")

    game=Game(ROOT_PATH,flags)
    game.setState(states.level())
    game.setScale(1)
    game.setScale()

    TILESIZE=game.getTileSize()

    levelPaths, levelNames, levelCount=loadlevels(ROOT_PATH+"\\level")


    classes = [
        "Shell_TrayWnd",      # main taskbar
        "Shell_SecondaryTrayWnd"  # secondary monitor taskbars
    ]
    user32 = ctypes.WinDLL("user32")
    SW_HIDE = 0
    SW_SHOW = 5

    #taskbar hide
    def hideTaskBar():
        for cls in classes:
            hwnd = user32.FindWindowW(cls, None)
            while hwnd:
                user32.ShowWindow(hwnd, SW_HIDE)
                hwnd = user32.FindWindowExW(0, hwnd, cls, None)

    def showTaskBar():
        for cls in classes:
            hwnd = user32.FindWindowW(cls, None)
            while hwnd:
                user32.ShowWindow(hwnd, SW_SHOW)
                hwnd = user32.FindWindowExW(0, hwnd, cls, None)


    #pyautogui.alert("Don't worry! Everything is working as intended.") #this needs to look better and be show at better time



    c=1
    for level in levelPaths:
        game.addLevel({f"level{c}":load_json(level)})
        c+=1
    game.loadLevel("level1")

    pcSSize=pygame.display.get_desktop_sizes()
    availableScreenSpace=[sum(i[0] for i in pcSSize),min(i[1] for i in pcSSize)]


    hideTaskBar()

    try:
        while game.getRun():
            game.frameStart=time.perf_counter()

            game.update()

            game.frameEnd=time.perf_counter()
            if game.sleepTime() > 0:
                time.sleep(game.sleepTime())
            #time.sleep(1/10)
    except Exception as e:
        if game.getFlag("showOkMessages"):
            pyautogui.alert("Oh no! An error acured! :(\nCheck the \\debug\\crash_reports folder for further information.")
        writeLog("crash",traceback.format_exc(),"crash_log",False,True,"w","main.py","main")


    showTaskBar()

isDev=False
devType=1
if isDev:
    if devType==0:
        from pycallgraph2 import PyCallGraph
        from pycallgraph2.output import GraphvizOutput
        graphviz = GraphvizOutput()
        graphviz.tool = r"C:\Program Files\Graphviz\bin\dot.exe"
        graphviz.output_file = r"D:\python\mm_w_pygame\helpers\dev_help\callgraph.png"
        print("Profiling with pycallgraph2")
        with PyCallGraph(output=graphviz):
            main()
    elif devType==1:
        import cProfile
        import pstats
        import io
        pr = cProfile.Profile()
        pr.enable()
        print("Profiling with cProfile")
        main()
        pr.disable()
        stream = io.StringIO()
        stats = pstats.Stats(pr, stream=stream)
        stats.sort_stats('cumtime')
        stats.print_stats()
        writeLog("log",stream.getvalue(),"profile",True,True,"w","main.py")
    else:
        print("No profiling. Running normaly. (incorrect devType)")
        main()
else:
    main()

