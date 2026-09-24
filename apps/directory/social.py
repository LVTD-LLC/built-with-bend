"""Bounded, network-free rendering of public project share cards."""

import hashlib
import json
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_ROOT = Path(__file__).with_name("fonts")
RENDER_VERSION = "1"
BACKGROUND, INK, MUTED, ACCENT = "#fbf8f4", "#3d3935", "#706860", "#ba442b"


def project_card_content(project):
    # Bound work even for records inserted without model validation.
    return (
        " ".join(project.title[:120].split()),
        " ".join(project.description[:3000].split()),
        " ".join(project.author[:120].split()),
        project.get_category_display()[:80],
    )


def project_card_version(content):
    payload = json.dumps((RENDER_VERSION, *content), ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:24]


@lru_cache(maxsize=32)
def font(size, style="regular"):
    filename = {"regular": "DejaVuSans", "bold": "DejaVuSans-Bold", "italic": "DejaVuSerif-Italic"}[
        style
    ]
    return ImageFont.truetype(str(FONT_ROOT / f"{filename}.ttf"), size)


def text_lines(text, face, width, limit):
    """Wrap even unbroken words; ellipsize the final line to its pixel budget."""
    lines = []
    remaining = text.strip()
    while remaining and len(lines) < limit:
        end = 0
        for index in range(1, len(remaining) + 1):
            if face.getlength(remaining[:index]) > width:
                break
            end = index
        if end == len(remaining):
            lines.append(remaining)
            remaining = ""
            break
        split = remaining.rfind(" ", 0, end + 1)
        end = split if split > 0 else max(end, 1)
        lines.append(remaining[:end].rstrip())
        remaining = remaining[end:].lstrip()
    if remaining:
        last = lines[-1]
        while last and face.getlength(last + "…") > width:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines


@lru_cache(maxsize=64)
def render_project_card(content):
    """Cache only a bounded number of images; callers enforce publication state."""
    title, description, author, category = content
    image = Image.new("RGB", (1200, 630), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((52, 46, 101, 95), radius=6, fill=ACCENT)
    draw.text((58, 45), "b.", font=font(37, "italic"), fill="#fffdf9")
    draw.text((114, 56), "builtwithbend", font=font(25, "bold"), fill=INK)
    label = text_lines(category, font(22), 450, 1)
    if label:
        draw.text((1148, 58), label[0], font=font(22), fill=MUTED, anchor="ra")

    title = title or "A Bend project"
    for size in (76, 68, 60, 52, 48):
        face = font(size, "bold")
        lines = text_lines(title, face, 800, 3)
        if not lines[-1].endswith("…") and len(lines) * (size + 8) <= 210:
            break
    description_lines = text_lines(description, font(27), 800, 3)
    content_height = len(lines) * (size + 8) + 18 + len(description_lines) * 36
    y = 130 + max(0, (370 - content_height) // 2)
    for line in lines:
        draw.text((52, y), line, font=face, fill=INK)
        y += size + 8
    y += 18
    for line in description_lines:
        draw.text((52, y), line, font=font(27), fill=MUTED)
        y += 36
    # The directory's outbound-link motif occupies its own column.
    draw.line((927, 398, 1138, 204), fill=ACCENT, width=7)
    draw.line((1061, 224, 1138, 204, 1110, 279), fill=ACCENT, width=7)

    draw.line((52, 531, 1148, 531), fill="#e5ddd4", width=1)
    attribution = f"Built by {author}" if author else "Explore this Bend 2 build"
    draw.text((52, 556), text_lines(attribution, font(22), 730, 1)[0], font=font(22), fill=ACCENT)
    draw.text((1148, 556), "builtwithbend.com", font=font(21), fill=MUTED, anchor="ra")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
