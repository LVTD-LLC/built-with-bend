"""Refresh the web assets and shared project-card background from the approved media kit."""

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "frontend" / "src"
BRAND = SRC / "brand"
DIRECTORY = ROOT / "apps" / "directory"
PAPER, INK, CLAY = "#fbf8f4", "#3d3935", "#ba442b"

# Two deliberately short lines keep the editorial headlines clear of the sculpture.
HEADLINES = {
    "blog": ("Stories from", "the directory."),
    "guides": ("Explore the", "Bend 2 guides."),
    "submit": ("Made with Bend?", "Share your build."),
    "bend-2-projects": ("What can you build", "with Bend 2?"),
}


def main():
    with ZipFile(BRAND / "built-with-bend-media-kit.zip") as kit:

        def asset(path):
            return kit.read("built-with-bend-media-kit/" + path)

        for name in ("logo-primary.svg", "logo-reverse.svg"):
            (BRAND / name).write_bytes(asset("logos/" + name))
        for name in (
            "favicon.ico",
            "apple-touch-icon.png",
            "android-192.png",
            "android-512.png",
            "site.webmanifest",
        ):
            (BRAND / name).write_bytes(asset("icons/" + name))
        (SRC / "icon.svg").write_bytes(asset("icons/favicon.svg"))
        logo = Image.open(BytesIO(asset("logos/logo-primary.png"))).convert("RGBA")
        paper = Image.open(BytesIO(asset("source/folded-paper.jpg"))).convert("RGB")
        cover = Image.open(BytesIO(asset("social/link-preview.jpg"))).convert("RGB")

    social = SRC / "social"
    cover.quantize().save(social / "directory.png")
    logo.thumbnail((310, 60), Image.Resampling.LANCZOS)
    regular = ImageFont.truetype(DIRECTORY / "fonts/InstrumentSerif-Regular.ttf", 94)
    italic = ImageFont.truetype(DIRECTORY / "fonts/InstrumentSerif-Italic.ttf", 100)
    caption = ImageFont.truetype(DIRECTORY / "fonts/DejaVuSans.ttf", 24)
    for name, (first, second) in HEADLINES.items():
        card = paper.resize((1260, 630), Image.Resampling.LANCZOS).crop((50, 0, 1250, 630))
        card.paste(logo, (58, 48), logo)
        draw = ImageDraw.Draw(card)
        draw.text((61, 300), first, font=regular, anchor="ls", fill=INK)
        draw.text((61, 405), second, font=italic, anchor="ls", fill=CLAY)
        draw.text((62, 559), "builtwithbend.com", font=caption, anchor="ls", fill=INK)
        card.quantize().save(social / f"{name}.png")

    # One shared plate for every listing. Only the text is rendered per request.
    plate = Image.new("RGB", (1200, 630), PAPER)
    plate.paste(logo, (52, 42), logo)
    panel = paper.resize((384, 630), Image.Resampling.LANCZOS, box=(1070, 0, 1611, 887))
    plate.paste(panel, (816, 0))
    plate.quantize(colors=96).save(DIRECTORY / "artwork/project-card.png")


if __name__ == "__main__":
    main()
