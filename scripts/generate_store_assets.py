#!/usr/bin/env python3
"""Generate Splash Zone's store artwork and representative SceneGraph previews."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
WIDTH = 1920
HEIGHT = 1080

FISH = (
    (245, 229, 232, 255),
    (255, 209, 102, 255),
    (255, 143, 112, 255),
    (185, 167, 255, 255),
)


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
    candidates = (
        Path("C:/Windows/Fonts") / font_name,
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        Path("/System/Library/Fonts") / "Helvetica.ttc",
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def draw_box(
    draw: ImageDraw.ImageDraw,
    origin: tuple[float, float],
    size: tuple[float, float],
    scale: float,
    color: tuple[int, int, int, int],
    angle: float = 0,
) -> None:
    x, y = origin
    width, height = size
    x, y, width, height = x * scale, y * scale, width * scale, height * scale
    center_x, center_y = x + width / 2, y + height / 2
    radians = math.radians(-angle)
    cosine, sine = math.cos(radians), math.sin(radians)
    points = []
    for dx, dy in (
        (-width / 2, -height / 2),
        (width / 2, -height / 2),
        (width / 2, height / 2),
        (-width / 2, height / 2),
    ):
        points.append(
            (
                center_x + dx * cosine - dy * sine,
                center_y + dx * sine + dy * cosine,
            )
        )
    draw.polygon(points, fill=color)


def draw_scene_fish(
    image: Image.Image,
    position: tuple[int, int],
    scale: float,
    color: tuple[int, int, int, int],
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    ox, oy = position
    segments = (
        ((14, 34), (88, 4), 0),
        ((14, 17), (47, 4), -25),
        ((53, 17), (47, 4), 25),
        ((14, 51), (47, 4), 25),
        ((53, 51), (47, 4), -25),
        ((94, 18), (31, 4), -39),
        ((94, 50), (31, 4), 39),
        ((19, 31), (6, 6), 0),
    )
    for (x, y), (width, height), angle in segments:
        draw_box(
            draw,
            (ox + x * scale, oy + y * scale),
            (width * scale, height * scale),
            1,
            color,
            angle,
        )
    image.alpha_composite(layer)


def draw_bubble(
    image: Image.Image,
    x: int,
    y: int,
    scale: float = 1,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    color = (142, 216, 232, 255)
    highlight = (197, 242, 247, 255)
    pieces = (
        (0, 4, 4, 18, color),
        (20, 4, 4, 18, color),
        (4, 0, 16, 4, color),
        (4, 22, 16, 4, color),
        (5, 6, 4, 4, highlight),
    )
    for ox, oy, width, height, piece_color in pieces:
        draw.rectangle(
            (
                round(x + ox * scale),
                round(y + oy * scale),
                round(x + (ox + width) * scale - 1),
                round(y + (oy + height) * scale - 1),
            ),
            fill=piece_color,
        )
    image.alpha_composite(layer)


def draw_seaweed(
    image: Image.Image,
    origin: tuple[int, int],
    stalks: tuple[tuple[int, int, int, int, int, tuple[int, int, int]], ...],
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    ox, oy = origin
    for x, y, width, height, angle, rgb in stalks:
        draw_box(
            draw,
            (ox + x, oy + y),
            (width, height),
            1,
            (*rgb, 255),
            angle,
        )
    image.alpha_composite(layer)


def render_scene(variant: int, store_artwork: bool = False) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), "#06243f")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 170, WIDTH, 390), fill="#0a3552")
    draw.rectangle((0, 500, WIDTH, 800), fill="#0a2e4a")
    draw.rectangle((0, 925, WIDTH, HEIGHT), fill="#102b3d")
    draw.rectangle((0, 170, WIDTH, 172), fill="#2b7990")
    draw.rectangle((0, 510, WIDTH, 511), fill="#20506a")
    draw.rectangle((0, 795, WIDTH, 796), fill="#1d4960")

    seaweed = (
        (
            (20, 0, 15, 170, -7, (36, 124, 112)),
            (0, 35, 12, 125, 23, (49, 146, 122)),
            (55, 25, 12, 145, -24, (45, 136, 117)),
            (83, 75, 10, 95, 18, (36, 124, 112)),
        ),
        (
            (15, 0, 13, 145, 9, (42, 138, 117)),
            (0, 38, 11, 112, -25, (39, 121, 104)),
            (45, 25, 11, 125, 26, (50, 145, 122)),
        ),
        (
            (20, 0, 14, 155, -8, (40, 127, 112)),
            (0, 30, 11, 120, 25, (49, 146, 122)),
            (53, 20, 12, 135, -23, (36, 119, 104)),
            (80, 70, 10, 90, 19, (42, 136, 116)),
        ),
        (
            (15, 0, 12, 125, 10, (45, 138, 117)),
            (0, 32, 10, 100, -24, (36, 119, 104)),
            (40, 28, 10, 100, 24, (49, 146, 122)),
        ),
    )
    for origin, stalks in zip(
        ((135, 900), (540, 930), (1440, 920), (1740, 945)),
        seaweed,
    ):
        draw_seaweed(image, origin, stalks)

    fish_positions = [
        (260 + variant * 82, 282 - variant * 14, 1.25, FISH[0]),
        (650 + variant * 115, 500 + variant * 8, 0.8, FISH[1]),
        (1120 - variant * 95, 705 - variant * 12, 1.05, FISH[2]),
        (1490 - variant * 110, 388 + variant * 22, 0.62, FISH[3]),
    ]
    if store_artwork:
        x, y, fish_scale, fish_color = fish_positions[0]
        fish_positions[0] = (x + 200, y + 150, fish_scale, fish_color)
    for x, y, scale, color in fish_positions:
        draw_scene_fish(image, (x, y), scale, color)

    bubble_positions = (
        (305 + variant * 34, 660 - variant * 125, 1),
        (785 - variant * 45, 370 + variant * 118, 1.3),
        (1158 + variant * 38, 585 - variant * 93, 0.75),
        (1568 - variant * 25, 248 + variant * 142, 1.15),
    )
    for x, y, scale in bubble_positions:
        draw_bubble(image, x, y, scale)

    return image.convert("RGB")


def make_store_artwork(scene: Image.Image) -> Image.Image:
    crop_left = (WIDTH - round(HEIGHT * 4 / 3)) // 2
    artwork = (
        scene.crop((crop_left, 0, crop_left + 1440, HEIGHT))
        .convert("RGBA")
        .resize((1080, 810), Image.Resampling.LANCZOS)
    )
    overlay = Image.new("RGBA", artwork.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle(
        (52, 48, 1028, 258),
        radius=34,
        fill=(4, 22, 39, 218),
        outline=(71, 151, 168, 230),
        width=3,
    )
    draw.ellipse((87, 100, 183, 196), outline=(120, 229, 232, 255), width=7)
    draw.arc((109, 122, 161, 174), start=200, end=20, fill=(120, 229, 232, 255), width=5)
    draw.line((124, 148, 151, 148), fill=(120, 229, 232, 255), width=5)
    draw.text((215, 72), "SPLASH ZONE", font=load_font(76, bold=True), fill="#f3fcff")
    draw.text(
        (220, 166),
        "A little underwater calm",
        font=load_font(37),
        fill="#a9e7ef",
    )
    artwork.alpha_composite(overlay)
    return artwork.convert("RGB").resize((540, 405), Image.Resampling.LANCZOS)


def main() -> None:
    screenshots_dir = ASSETS / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    store_dir = ASSETS / "store"
    store_dir.mkdir(parents=True, exist_ok=True)

    scenes = [render_scene(variant) for variant in range(3)]
    for index, scene in enumerate(scenes, start=1):
        destination = screenshots_dir / f"SplashZone-Screenshot-{index:02d}-1920x1080.png"
        scene.save(destination, format="PNG", optimize=True)
        print(f"Created {destination.relative_to(ROOT)} ({WIDTH}x{HEIGHT})")

    artwork = make_store_artwork(render_scene(0, store_artwork=True))
    destination = store_dir / "SplashZone-Store-540x405.png"
    artwork.save(destination, format="PNG", optimize=True)
    print(f"Created {destination.relative_to(ROOT)} (540x405)")


if __name__ == "__main__":
    main()
