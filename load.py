import json


def load_json(filePath:str):
    if filePath.endswith(".json"):
        with open(filePath,"r") as f:
            return json.load(f)
    else:
        print("Incorrect file format!")
        print(f"Path was: {filePath}")
        return 1