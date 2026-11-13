"""Turn a photo or ASCII portrait into ASCII text art (bright areas = dense characters).
Run once on your computer (needs: pip install opencv-python-headless numpy):
    python scripts/make_portrait.py [photo.png] [cols]
Writes data/portrait.txt. Change CROP to frame your face."""
import sys
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
src = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "portrait.png")
cols = int(sys.argv[2]) if len(sys.argv) > 2 else 56
RAMP = " .,:;-=+*#%@"

# Default crop calibrated for the portrait in data/portrait.png: (left, top, right, bottom)
# Adjust if using a different photo
img_raw = cv2.imread(src, cv2.IMREAD_GRAYSCALE)
if img_raw is None:
    raise SystemExit(f"Could not open image: {src}")

h, w = img_raw.shape
if w > 2000:
    # High-resolution ASCII export (e.g. 3714 x 3260)
    CROP = (950, 680, 2750, 2480)
    blur_k = 23
else:
    # Standard photo crop
    CROP = (int(w * 0.25), int(h * 0.2), int(w * 0.75), int(h * 0.75))
    blur_k = 5

left, top, right, bottom = CROP
img = img_raw[top:bottom, left:right]
rows = 31  # matches the 354x330 portrait panel in hero card

# Smooth character dots into continuous tones if needed
smooth = cv2.GaussianBlur(img, (blur_k, blur_k), 0)
clahe = cv2.createCLAHE(clipLimit=2.8, tileGridSize=(8, 8))
enhanced = clahe.apply(smooth) / 255.0
bg = cv2.GaussianBlur(smooth, (81, 81), 0) / 255.0
enhanced = enhanced * np.clip((bg - 15 / 255.0) / 0.05, 0, 1)
enhanced = np.clip(enhanced * 1.25, 0, 1) ** 1.05

resized = cv2.resize(enhanced, (cols, rows), interpolation=cv2.INTER_AREA)
lines = ["".join(RAMP[int(min(v, 1) * (len(RAMP) - 1))] for v in row).rstrip() for row in resized]

out_file = ROOT / "data" / "portrait.txt"
out_file.write_text("\n".join(lines))
print(f"Generated {out_file} ({cols} x {rows}) from {src}")
