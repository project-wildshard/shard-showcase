"""Create matched portrait plates with the CSS palette and the actual cap anchors."""
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

out = Path(sys.argv[1])
font = sys.argv[2]
anchors = json.loads((out / "anchors.json").read_text())
plate = Image.open(out / "marker-plate.png").convert("RGBA")
assert plate.size == (804, 1748)
palette = {"locked": ("!", "#a7aeb2", "#1b1f22"),
           "available": ("!", "#ffd54a", "#2a1a02"),
           "turnIn": ("?", "#ffd54a", "#2a1a02")}
rows = {}

def marker(image, role, label, state):
    glyph, fill, outline = palette[state]
    head_x, head_y = [round(2 * anchors[role][k]) for k in ("headX", "headY")]
    face, caption = ImageFont.truetype(font, 80), ImageFont.truetype(font, 16)
    x0, y0, x1, y1 = face.getbbox(glyph, stroke_width=3)
    gx, gy = round(head_x - (x0+x1)/2), head_y - 8 - y1
    a, b, c, d = caption.getbbox(label)
    lx, ly = round(head_x - (a+c)/2), gy + y0 - 5 - d
    bounds = [min(gx+x0,lx+a),ly+b,max(gx+x1,lx+c),gy+y1]
    assert bounds[3] == head_y-8 and bounds[0] > 0 and bounds[2] < 804
    assert 0 < bounds[1] < bounds[3] < 1748
    ink = Image.new("RGBA", image.size)
    pen = ImageDraw.Draw(ink)
    pen.text((gx, gy), glyph, font=face, fill=fill, stroke_fill=outline, stroke_width=3)
    pen.text((lx, ly), label, font=caption, fill="#f2f4ed", stroke_fill="#24231e", stroke_width=1)
    glow = Image.new("RGBA", image.size, "#12100c")
    glow.putalpha(ink.getchannel("A").filter(ImageFilter.GaussianBlur(5)))
    image.alpha_composite(glow)
    image.alpha_composite(ink)
    return {"state": state, "glyph": glyph, "color": fill, "outlined_bounds_px": bounds}

for shot, state in [("offer", "available"), ("turn-in", "turnIn"), ("cleared", None)]:
    im = plate.copy()
    placed = {"surveyor": marker(im, "surveyor", "SURVEYOR", "locked")}
    if state:
        placed["yard-boss"] = marker(im, "yard-boss", "YARD BOSS", state)
        assert placed["surveyor"]["outlined_bounds_px"][2]+60 < placed["yard-boss"]["outlined_bounds_px"][0]
    im.convert("RGB").save(out / f"quest-{shot}.webp", quality=88, method=6)
    rows[shot] = placed

(out / "w1b-quest-marker-proof.json").write_text(json.dumps({
    "scope": "Blender plate and raster UI proof; not running game",
    "viewport_css_px": [402,874], "output_px": [804,1748], "eye_height_m": 1.7,
    "outlined_glyph_clearance_css_px": 4,
    "archive_style_blob": "297dff6669b7ac8c15239b30833338144cbee418",
    "anchors": anchors, "states": rows
}, indent=2)+"\n")
