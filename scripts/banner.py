#!/usr/bin/env python3
"""Generate assets/banner.png for the README header.

Deps:
    pip install Pillow svgpathtools numpy

Run (from repo root, or anywhere -- paths are resolved relative to this file):
    python scripts/banner.py

Optional: also composite the banner onto light/dark backgrounds for preview
(NOT committed -- writes outside the repo):
    python scripts/banner.py --preview "C:\\path\\to\\output\\dir"

The script is deterministic: no randomness is used anywhere.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from svgpathtools import svg2paths

# ---------------------------------------------------------------------------
# Paths (all relative to this file, not the cwd)
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
ASSETS_DIR = REPO_ROOT / "assets"
FONTS_DIR = HERE / "fonts"
ICON_SVG = ASSETS_DIR / "icon-yellow.svg"
ROCKY_WEBP = ASSETS_DIR / "rocky.webp"
OUT_PNG = ASSETS_DIR / "banner.png"

JURA_TTF = FONTS_DIR / "Jura.ttf"
INTER_TTF = FONTS_DIR / "Inter-Variable.ttf"

# ---------------------------------------------------------------------------
# Palette (from portfolio src/index.css)
# ---------------------------------------------------------------------------
BG_TOP = (5, 5, 5)        # #050505
BG_BOTTOM = (0, 0, 0)     # #000
YELLOW = (255, 206, 26)   # #ffce1a
BEIGE = (216, 201, 168)   # #d8c9a8
BLUE = (91, 174, 255)     # #5baeff
LAVENDER = (185, 166, 255)  # #b9a6ff

# ---------------------------------------------------------------------------
# Canvas geometry -- rendered at SS supersample, downsampled at the end
# ---------------------------------------------------------------------------
FINAL_W, FINAL_H = 1600, 400
SS = 4
W, H = FINAL_W * SS, FINAL_H * SS
CORNER_RADIUS = 18 * SS


def load_font(path: Path, size: int, variation: str | None = None) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(path), size)
    if variation is not None:
        try:
            font.set_variation_by_name(variation)
        except Exception:
            pass
    return font


# ---------------------------------------------------------------------------
# SVG -> rasterized yellow mark (no cairosvg available; parse + rasterize by
# hand using svgpathtools to flatten beziers, then fill via even-odd XOR
# compositing across subpaths so holes / cutouts render correctly).
# ---------------------------------------------------------------------------
def rasterize_icon(target_h_px: int) -> Image.Image:
    paths, _attrs = svg2paths(str(ICON_SVG))
    path = paths[0]

    # Split the single compound Path into its disjoint/nested subpaths (each
    # run of segments between M-jumps).
    subpaths: list[list] = []
    cur = [path[0]]
    for seg in path[1:]:
        if abs(seg.start - cur[-1].end) > 1e-6:
            subpaths.append(cur)
            cur = [seg]
        else:
            cur.append(seg)
    subpaths.append(cur)

    xmin, xmax, ymin, ymax = path.bbox()
    src_w, src_h = xmax - xmin, ymax - ymin

    # Render at a comfortably high resolution for crisp downsampling.
    render_h = target_h_px * SS
    render_w = int(round(render_h * src_w / src_h))
    scale = render_h / src_h

    mask = Image.new("1", (render_w, render_h), 0)
    for sp in subpaths:
        pts = []
        for seg in sp:
            # sample each segment; more samples for curves, fewer for lines
            n = 2 if seg.__class__.__name__ == "Line" else 24
            for i in range(n):
                t = i / n
                z = seg.point(t)
                x = (z.real - xmin) * scale
                y = (z.imag - ymin) * scale
                pts.append((x, y))
        if len(pts) < 3:
            continue
        sub_mask = Image.new("1", (render_w, render_h), 0)
        ImageDraw.Draw(sub_mask).polygon(pts, fill=1)
        mask = Image.frombuffer(
            "1", mask.size, bytes(a ^ b for a, b in zip(mask.tobytes(), sub_mask.tobytes()))
        )

    icon = Image.new("RGBA", (render_w, render_h), (0, 0, 0, 0))
    solid = Image.new("RGBA", (render_w, render_h), YELLOW + (255,))
    icon = Image.composite(solid, icon, mask.convert("L").point(lambda v: 255 if v else 0))

    # Downsample for anti-aliased edges, back down toward final banner scale.
    final_h = target_h_px
    final_w = int(round(final_h * src_w / src_h))
    icon = icon.resize((final_w, final_h), Image.LANCZOS)
    return icon


# ---------------------------------------------------------------------------
# Text helpers -- manual letter-spacing (Pillow has no native tracking)
# ---------------------------------------------------------------------------
def draw_tracked_text(draw, xy, text, font, fill, tracking=0, anchor_left=True):
    x, y = xy
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1 if len(text) > 1 else 0)
    if not anchor_left:
        x -= total
    cx = x
    for ch, w in zip(text, widths):
        draw.text((cx, y), ch, font=font, fill=fill)
        cx += w + tracking
    return total


def tracked_text_width(draw, text, font, tracking=0):
    widths = [draw.textlength(ch, font=font) for ch in text]
    return sum(widths) + tracking * (len(text) - 1 if len(text) > 1 else 0)


# ---------------------------------------------------------------------------
# Background: gradient + fine grid + radial glow + vignette
# ---------------------------------------------------------------------------
def build_background() -> Image.Image:
    # Vertical gradient BG_TOP -> BG_BOTTOM (very subtle -- both are near-black),
    # built as a 1px-wide column and stretched, to avoid a per-pixel loop.
    grad = Image.new("RGB", (1, H))
    gpx = grad.load()
    for y in range(H):
        t = y / (H - 1)
        gpx[0, y] = (
            int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t),
            int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t),
            int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t),
        )
    img = grad.resize((W, H))

    # Fine grid, very low alpha, for depth/texture.
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid)
    step = 40 * SS
    grid_color = BEIGE + (10,)
    for x in range(0, W, step):
        gdraw.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H, step):
        gdraw.line([(0, y), (W, y)], fill=grid_color, width=1)
    img = Image.alpha_composite(img.convert("RGBA"), grid)

    # Radial glow centered slightly left-of-middle (behind the logo/title),
    # warm yellow, soft falloff.
    glow = Image.new("L", (W, H), 0)
    gdraw = ImageDraw.Draw(glow)
    cx, cy = int(W * 0.30), int(H * 0.5)
    max_r = int(H * 1.15)
    steps = 60
    for i in range(steps, 0, -1):
        r = int(max_r * i / steps)
        alpha = int(46 * (1 - i / steps) ** 1.6)
        bbox = [cx - r, cy - r, cx + r, cy + r]
        gdraw.ellipse(bbox, fill=alpha)
    glow_rgba = Image.merge(
        "RGBA",
        (
            Image.new("L", (W, H), YELLOW[0]),
            Image.new("L", (W, H), YELLOW[1]),
            Image.new("L", (W, H), YELLOW[2]),
            glow,
        ),
    )
    img = Image.alpha_composite(img, glow_rgba)

    # Vignette: darken toward the outer edges/corners.
    vign = Image.new("L", (W, H), 0)
    vdraw = ImageDraw.Draw(vign)
    vcx, vcy = W // 2, H // 2
    vmax_r = int(math.hypot(W, H) / 2)
    steps = 50
    for i in range(steps):
        r = int(vmax_r * (0.55 + 0.45 * i / steps))
        alpha = int(120 * (i / steps) ** 2)
        bbox = [vcx - r, vcy - r, vcx + r, vcy + r]
        vdraw.ellipse(bbox, fill=alpha)
    vign_rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vign_rgba.putalpha(vign)
    black_layer = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    black_layer.putalpha(vign)
    img = Image.alpha_composite(img, black_layer)

    return img


def apply_rounded_transparent_corners(img: Image.Image) -> Image.Image:
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, W - 1, H - 1], radius=CORNER_RADIUS, fill=255
    )
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def draw_inner_border(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    inset = SS  # ~1px at final scale
    draw.rounded_rectangle(
        [inset, inset, W - 1 - inset, H - 1 - inset],
        radius=CORNER_RADIUS - inset,
        outline=YELLOW + (64,),  # rgba(255,206,26,0.25)
        width=SS,
    )


def build_banner() -> Image.Image:
    img = build_background()
    draw = ImageDraw.Draw(img)

    # --- pieces: icon | rule | text block | rule | rocky, centered as one
    # group with equal side margins -----------------------------------------
    icon_h = int(H * 0.54)
    icon = rasterize_icon(icon_h)

    rocky_h = int(H * 0.60)
    rocky_src = Image.open(ROCKY_WEBP).convert("RGBA")
    rocky_w = int(round(rocky_h * rocky_src.width / rocky_src.height))
    rocky = rocky_src.resize((rocky_w, rocky_h), Image.LANCZOS)

    title = "KRISH PUNJABI"
    title_font = load_font(JURA_TTF, int(84 * SS), variation="Medium")
    tracking = int(8 * SS)
    title_w = tracked_text_width(draw, title, title_font, tracking=tracking)

    tagline = "software engineering @ uwaterloo  ·  building praxic"
    tag_font = load_font(INTER_TTF, int(30 * SS), variation="Regular")
    tag_tracking = int(1.2 * SS)
    tag_w = tracked_text_width(draw, tagline, tag_font, tracking=tag_tracking)

    text_block_w = max(title_w, tag_w)

    gap_icon_rule = int(W * 0.035)
    gap_rule_text = int(W * 0.03)
    gap_text_rule = int(W * 0.03)
    gap_rule_rocky = int(W * 0.035)

    total_w = int(round(
        icon.width + gap_icon_rule + gap_rule_text + text_block_w
        + gap_text_rule + gap_rule_rocky + rocky.width
    ))

    content_left = (W - total_w) // 2
    content_top = (H - icon_h) // 2

    icon_x = content_left
    img.alpha_composite(icon, (icon_x, content_top))

    rule_w = max(2, 3 * SS)
    rule_top = content_top + int(icon_h * 0.06)
    rule_bottom = content_top + icon_h - int(icon_h * 0.06)

    def draw_rule(x: int) -> None:
        nonlocal img
        glow_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_img)
        gdraw.line([(x, rule_top), (x, rule_bottom)], fill=YELLOW + (255,), width=rule_w)
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(6 * SS))
        img = Image.alpha_composite(img, glow_img)
        ImageDraw.Draw(img).line(
            [(x, rule_top), (x, rule_bottom)], fill=YELLOW + (255,), width=rule_w
        )

    rule1_x = icon_x + icon.width + gap_icon_rule
    draw_rule(rule1_x)

    text_x = rule1_x + gap_rule_text

    # --- title: KRISH PUNJABI, Jura, beige, letter-spaced -----------------
    draw = ImageDraw.Draw(img)
    title_y = content_top + int(icon_h * 0.10)
    title_x = text_x + (text_block_w - title_w) // 2
    draw_tracked_text(draw, (title_x, title_y), title, title_font, BEIGE + (255,), tracking=tracking)

    # --- tagline: Inter, muted, below title --------------------------------
    tag_y = title_y + int(84 * SS * 1.28)
    tag_color = (198, 198, 198, 255)
    tag_x = text_x + (text_block_w - tag_w) // 2
    draw_tracked_text(draw, (tag_x, tag_y), tagline, tag_font, tag_color, tracking=tag_tracking)

    # small accent underline under tagline start, echoing the rule color
    underline_y = tag_y + int(30 * SS * 1.9)
    underline_w = int(W * 0.14)
    underline_x = text_x + (text_block_w - underline_w) // 2
    draw.line(
        [(underline_x, underline_y), (underline_x + underline_w, underline_y)],
        fill=YELLOW + (140,),
        width=max(1, SS),
    )

    # second yellow bar, identical to the first, right of the text block
    rule2_x = int(round(text_x + text_block_w + gap_text_rule))
    draw_rule(rule2_x)

    # --- rocky, right of the second bar, vertically centered ---------------
    rocky_x = rule2_x + gap_rule_rocky
    rocky_top = (H - rocky.height) // 2
    img.alpha_composite(rocky, (rocky_x, rocky_top))

    img = apply_rounded_transparent_corners(img)
    draw_inner_border(img)

    img = img.resize((FINAL_W, FINAL_H), Image.LANCZOS)
    return img


def composite_on(bg_color, banner: Image.Image, pad: int = 60) -> Image.Image:
    canvas = Image.new("RGB", (banner.width + pad * 2, banner.height + pad * 2), bg_color)
    canvas.paste(banner, (pad, pad), banner)
    return canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", type=str, default=None, help="dir to write preview composites (not committed)")
    args = parser.parse_args()

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    banner = build_banner()
    banner.save(OUT_PNG)
    print(f"wrote {OUT_PNG}")

    if args.preview:
        out_dir = Path(args.preview)
        out_dir.mkdir(parents=True, exist_ok=True)
        light = composite_on((255, 255, 255), banner)
        dark = composite_on((13, 17, 23), banner)  # #0d1117
        light.save(out_dir / "banner-on-light.png")
        dark.save(out_dir / "banner-on-dark.png")
        print(f"wrote previews to {out_dir}")


if __name__ == "__main__":
    main()
