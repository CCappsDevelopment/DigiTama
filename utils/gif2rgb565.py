# gif2rgb565.py
from PIL import Image
from struct import pack
from os import path
import sys

def write_bin(f, pixel_list):
    for r8, g8, b8 in pixel_list:
        r = (r8 >> 3) & 0x1F
        g = (g8 >> 2) & 0x3F
        b = (b8 >> 3) & 0x1F
        f.write(pack('>H', (r << 11) + (g << 5) + b))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python gif2rgb565.py anim.gif")
        sys.exit(1)

    in_path = sys.argv[1]
    if not path.exists(in_path):
        print("File not found:", in_path)
        sys.exit(1)

    base, ext = path.splitext(in_path)
    im = Image.open(in_path)

    frame_index = 0
    while True:
        im.seek(frame_index)
        frame = im.convert("RGB").resize((128, 128))
        pixels = list(frame.getdata())
        out_path = f"{base}_{frame_index:02d}.raw"
        with open(out_path, "wb") as f:
            write_bin(f, pixels)
        print("Saved", out_path)
        frame_index += 1
        try:
            im.seek(frame_index)
        except EOFError:
            break

