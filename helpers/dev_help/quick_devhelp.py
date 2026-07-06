
import os



ROOT_PATH=os.path.dirname(os.path.abspath(__file__))

path="\\quick_devhelp.txt"
abc=["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
numbers=["0","1","2","3","4","5","6","7","8","9"]

with open(ROOT_PATH+path,"w") as f:
    for i in abc:
        f.write(f'pygame.K_{i}:"{i}",\n')

with open(ROOT_PATH+path,"w") as f:
    for i in numbers:
        f.write(f'pygame.K_{i}:"{i}",\n')