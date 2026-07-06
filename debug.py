

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_class.game_class import Game


import datetime
import os
#import traceback
from pathlib import Path

class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"

    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"

    END = "\033[0m"


def setupFolders():
    ROOT_PATH=os.path.dirname(os.path.abspath(__file__))
    folder = Path(ROOT_PATH+"\\debug")
    folder.mkdir(parents=True, exist_ok=True)
    folder = Path(ROOT_PATH+"\\playerdata")
    folder.mkdir(parents=True, exist_ok=True)
    folder = Path(ROOT_PATH+"\\debug\\crash_reports")
    folder.mkdir(parents=True, exist_ok=True)
    folder = Path(ROOT_PATH+"\\debug\\logs")
    folder.mkdir(parents=True, exist_ok=True)
    folder = Path(ROOT_PATH+"\\debug\\logs\\log_errors")
    folder.mkdir(parents=True, exist_ok=True)
    folder = Path(ROOT_PATH+"\\debug\\temp")
    folder.mkdir(parents=True, exist_ok=True)
    with open(ROOT_PATH+"\\debug\\README.txt","w") as f:
        f.write("Hello!\nIf you are looking for files to delete:\nYou can delete the debug and playerdata folders. These folders are automatically created with this README.\n\nThe debug folder is filled with logs, crash reports, and other boring stuff. These files are only important if you encounter a constant issue with the game.\nThe playerdata folder is for you save files if you no longer need them you can delete them.")

def writeLog(type:str, content:any, fileName:str, addNumber:bool=True, addDate:bool=True, writeType:str="w", fromFile:str="UNKNOWN", fromFunc:str="UNKNOWN"):
    """
        type: "crash"/"error", "log", "temp", "data" ("log_e" is not for you)

        content: what to write into the file (may be anything, if not supported: will be)

        fileName: the name of the file !!!Without the extention!!!

        addNumber: add 0,1,2,3,.. to end of file (can only write; can't append) (can only add number or date)

        addDate: add date and time at end of file (can only add number or date)

        writeType: "w", "a"

        fromFile: please include file name where this log originates from, for easier trace

        fromFunc: please include function name where this log originates from, for easier trace
    """
    ROOT_PATH=os.path.dirname(os.path.abspath(__file__))
    folderPath=ROOT_PATH
    fileExtention=".txt"
    if type=="crash" or type=="error":
        folderPath+="\\debug\\crash_reports"
        fileExtention="txt"
    elif type=="log":
        folderPath+="\\debug\\logs"
        fileExtention="log"
    elif type=="log_e":
        folderPath+="\\debug\\logs\\log_errors"
        fileExtention="log"
    elif type=="temp":
        folderPath+="\\debug\\temp"
        fileExtention="tmp"
    elif type=="data":
        folderPath+="\\playerdata"
        fileExtention="dat"
    else:
        writeLog("log_e",f"Log with unknown type from: {fromFile}; {fromFunc}\nWith type: {type}","LogError",True,False,"w","debug.py","writeLog")
        return


    if addNumber:
        folder = Path(folderPath)
        folder.mkdir(exist_ok=True)
        i = 0
        while True:
            filename = f"{fileName}{i}.{fileExtention}"
            filepath = folder / filename
            if not filepath.exists():
                if isinstance(content,list):
                    filepath.write_text("\n".join(str(i) for i in content)+"\nFrom file: "+fromFile+"; From function: "+fromFunc)
                else:
                    filepath.write_text(content+"\nFrom file: "+fromFile+"; From function: "+fromFunc)
                break
            i += 1
        return
    if addDate:
        fullPath=folderPath+"\\"+fileName+str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+"."+fileExtention
        with open(fullPath,writeType) as f:
            f.write(content)
            f.write("\n")
            f.write(fromFile)
            f.write("; ")
            f.write(fromFunc)

def printLog(type:str, content:any):
    extra=''
    if type=="warning":
        extra=Colors.RED
    elif type=="debug":
        extra=Colors.YELLOW
    extra+=Colors.BOLD
    print(extra+f"[{type.upper()}]"+Colors.END+f"  {content}")



setupFolders()