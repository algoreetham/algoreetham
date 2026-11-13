"""Turn a photo into ASCII text art (bright areas = dense characters).
Run once on your computer (needs: pip install opencv-python-headless numpy):
    python scripts/make_portrait.py photo.png [cols]
Writes data/portrait.txt. Change CROP to frame your face."""
import sys
import cv2
import numpy as np

src = sys.argv[1]
cols = int(sys.argv[2]) if len(sys.argv) > 2 else 56
CROP = (380, 530, 680, 880)  # left, top, right, bottom around the face
RAMP = " .,:;-=+*#%@"

left, top, right, bottom = CROP
img = cv2.imread(src, cv2.IMREAD_GRAYSCALE)[top:bottom, left:right]
rows = int(cols * (img.shape[0] / img.shape[1]) * 0.5)  # characters are about twice as tall as wide
img = cv2.resize(img, (cols * 6, rows * 6), interpolation=cv2.INTER_AREA)
bg = cv2.GaussianBlur(img, (0, 0), 6) / 255.0
a = cv2.createCLAHE(clipLimit=4, tileGridSize=(6, 6)).apply(img) / 255.0  # lifts detail in the dark face
a = a * np.clip((bg - 0.04) / 0.08, 0, 1)  # dark background stays blank
a = np.clip(a, 0, 1) ** 1.2
a = cv2.resize(a, (cols, rows), interpolation=cv2.INTER_AREA)
lines = ["".join(RAMP[int(min(v, 1) * (len(RAMP) - 1))] for v in row).rstrip() for row in a]
open("data/portrait.txt", "w").write("\n".join(lines))
print(cols, "x", rows)
