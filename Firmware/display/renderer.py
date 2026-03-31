# builds greyscale PIL images ready for the eink panel
# handles text wrapping, fonts, title/body/meta layout, splash + error screens

from PIL import Image, ImageDraw, ImageFont, ImageOps
from loguru import logger
from config.settings import DISPLAY_WIDTH, DISPLAY_HEIGHT, FONT_PATH, FONT_BOLD_PATH
import os

MARGIN           = 60
LINE_SPACING     = 8
TITLE_FONT_SIZE  = 64
BODY_FONT_SIZE   = 40
META_FONT_SIZE   = 30
DIVIDER_Y_OFFSET = 20

def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    logger.warning(f"font missing at {path}, using fallback")
    return ImageFont.load_default()

def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    words           = text.split()
    lines, current  = [], []
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines

def render_text(
    title: str,
    body: str,
    subreddit: str = "",
    score: int = 0,
    width: int = DISPLAY_WIDTH,
    height: int = DISPLAY_HEIGHT
) -> Image.Image:
    img        = Image.new("L", (width, height), 255)
    draw       = ImageDraw.Draw(img)
    font_title = _load_font(FONT_BOLD_PATH, TITLE_FONT_SIZE)
    font_body  = _load_font(FONT_PATH, BODY_FONT_SIZE)
    font_meta  = _load_font(FONT_PATH, META_FONT_SIZE)
    usable     = width - (MARGIN * 2)
    y          = MARGIN

    if subreddit:
        draw.text((MARGIN, y), f"r/{subreddit}  ·  ↑ {score:,}", font=font_meta, fill=100)
        y += META_FONT_SIZE + LINE_SPACING + DIVIDER_Y_OFFSET
        draw.line([(MARGIN, y), (width - MARGIN, y)], fill=180, width=1)
        y += DIVIDER_Y_OFFSET

    for line in _wrap_text(title, font_title, usable, draw):
        draw.text((MARGIN, y), line, font=font_title, fill=0)
        y += TITLE_FONT_SIZE + LINE_SPACING
    y += DIVIDER_Y_OFFSET * 2

    for line in _wrap_text(body, font_body, usable, draw):
        if y + BODY_FONT_SIZE > height - MARGIN:
            draw.text((MARGIN, y), "…", font=font_body, fill=80)
            break
        draw.text((MARGIN, y), line, font=font_body, fill=30)
        y += BODY_FONT_SIZE + LINE_SPACING

    footer_y = height - MARGIN - META_FONT_SIZE
    draw.line([(MARGIN, footer_y - DIVIDER_Y_OFFSET), (width - MARGIN, footer_y - DIVIDER_Y_OFFSET)], fill=180, width=1)
    draw.text((MARGIN, footer_y), "NEXUS-INK", font=font_meta, fill=150)
    return img

def render_image(
    source_image: Image.Image,
    width: int = DISPLAY_WIDTH,
    height: int = DISPLAY_HEIGHT
) -> Image.Image:
    img = source_image.convert("L")
    return ImageOps.fit(img, (width, height), method=Image.LANCZOS)

def render_error(
    message: str,
    width: int = DISPLAY_WIDTH,
    height: int = DISPLAY_HEIGHT
) -> Image.Image:
    img  = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(img)
    draw.text((MARGIN, height // 2 - TITLE_FONT_SIZE), "Error",
              font=_load_font(FONT_BOLD_PATH, TITLE_FONT_SIZE), fill=0)
    draw.text((MARGIN, height // 2 + LINE_SPACING), message,
              font=_load_font(FONT_PATH, BODY_FONT_SIZE), fill=60)
    return img

def render_splash(
    width: int = DISPLAY_WIDTH,
    height: int = DISPLAY_HEIGHT
) -> Image.Image:
    img      = Image.new("L", (width, height), 255)
    draw     = ImageDraw.Draw(img)
    font     = _load_font(FONT_BOLD_PATH, 120)
    bbox     = draw.textbbox((0, 0), "NEXUS-INK", font=font)
    x        = (width  - (bbox[2] - bbox[0])) // 2
    y        = (height - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), "NEXUS-INK", font=font, fill=0)
    font_sub = _load_font(FONT_PATH, META_FONT_SIZE)
    bbox2    = draw.textbbox((0, 0), "booting…", font=font_sub)
    draw.text(((width - (bbox2[2] - bbox2[0])) // 2, y + 140), "booting…", font=font_sub, fill=120)
    return img
