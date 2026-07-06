from pathlib import Path
from PIL import Image
import math
import time


def hex_to_rgb(hex_color: str):
    """Convert '#RRGGBB' or 'RRGGBB' to (R, G, B)."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_distance(c1, c2):
    """
    Euclidean RGB distance.
    Range: 0–441.67
    """
    return math.sqrt(
        (c1[0] - c2[0])**2 +
        (c1[1] - c2[1])**2 +
        (c1[2] - c2[2])**2
    )


def replace_color_in_pngs(folder_path: str,colorA: str,colorB: str,tolerance: float = 0):
    """
    Replace colors within tolerance distance of colorA
    with colorB in every PNG in the folder.
    
    tolerance examples:
        0   = exact match only
        10  = very strict
        30  = similar shades
        60  = broader range
        100 = large range
    """

    source_rgb = hex_to_rgb(colorA)
    target_rgb = hex_to_rgb(colorB)

    folder = Path(folder_path)

    if not folder.is_absolute():
        raise ValueError("folder_path must be absolute")

    if not folder.is_dir():
        raise ValueError(f"Folder not found: {folder}")

    for png_file in folder.glob("*.png"):
        print(f"Processing: {png_file.name}")

        img = Image.open(png_file).convert("RGBA")
        pixels = list(img.getdata())

        new_pixels = []

        for r, g, b, a in pixels:
            current = (r, g, b)

            if color_distance(current, source_rgb) <= tolerance:
                new_pixels.append((*target_rgb, a))
            else:
                new_pixels.append((r, g, b, a))

        img.putdata(new_pixels)
        img.save(png_file)  # overwrite original

    print("Done.")

print("WARNING!:\nAI generated code!")
time.sleep(2)
playergrap=False
hud=True
wep="dark"
b="#0070EC"
b2="#00E8D8"
if playergrap:
    PATH=r"D:\python\mm_w_pygame\sprite\player"+"\\"+wep
    replace_color_in_pngs(folder_path=PATH,colorA="#165370",colorB="#FFA600",tolerance=35)
    replace_color_in_pngs(folder_path=PATH,colorA="#00D5FF",colorB="#c0c0c0",tolerance=35)
if hud:
    PATH=r"D:\python\mm_w_pygame\sprite\hud\weapon"+"\\"+wep
    replace_color_in_pngs(
        folder_path=PATH,
        colorA="#FFF200",
        colorB="#3A3A3A",
        tolerance=35
    )
    replace_color_in_pngs(
        folder_path=PATH,
        colorA="#FEFFEF",
        colorB="#7F7F7F",
        tolerance=35
    )
