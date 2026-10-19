"""Embed snk's animated SVG into the profile card as a self-contained panel."""

import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET


START = "  <!-- CONTRIBUTION-SNAKE:START -->"
END = "  <!-- CONTRIBUTION-SNAKE:END -->"


def embed(snake_path: Path, card_path: Path) -> None:
    snake = snake_path.read_text(encoding="utf-8")
    snake_root = ET.fromstring(snake)
    if snake_root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("The snake input must be an SVG image")
    view_box = snake_root.attrib["viewBox"]
    body = re.search(r"<svg\b[^>]*>(.*)</svg>\s*$", snake, re.S).group(1)
    # In an inline SVG, :root would target the entire card. Keep the palette local.
    body = body.replace(":root", "#contribution-snake")
    panel = f'''{START}
  <g transform="translate(8, 574)" id="contributions-widget">
    <rect class="term-box" width="784" height="200" />
    <text x="6" y="14" class="plus-mark">+</text>
    <text x="772" y="14" class="plus-mark">+</text>
    <text x="24" y="28" font-family="'Inter Tight', 'Inter', sans-serif" font-size="11" letter-spacing="2" fill="#7a7a7a">[ CONTRIBUTION SNAKE ]</text>
    <text x="760" y="28" text-anchor="end" font-family="monospace" font-size="9" fill="#7a7a7a">LAST 12 MONTHS</text>
    <svg id="contribution-snake" x="16" y="32" width="752" height="164" viewBox="{view_box}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Animated snake eating Aboubakr Tahir's GitHub contributions">
      {body}
    </svg>
  </g>
{END}'''

    card = card_path.read_text(encoding="utf-8")
    if START in card:
        start = card.index(START)
        end = card.index(END, start) + len(END)
        card = card[:start] + panel + card[end:]
    else:
        end = card.rindex("</svg>")
        card = card[:end] + panel + "\n" + card[end:]

    opening = re.search(r"<svg\b[^>]*>", card).group(0)
    resized = re.sub(r'\bheight="[^"]*"', 'height="784"', opening)
    resized = re.sub(r'\bviewBox="[^"]*"', 'viewBox="0 0 800 784"', resized)
    card = card.replace(opening, resized, 1)
    card = re.sub(
        r'(<rect width="800" height=")[^"]*(" fill="#060606" rx="0" />)',
        r'\g<1>784\2',
        card,
        count=1,
    )
    ET.fromstring(card)
    card_path.write_text(card, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snake", type=Path)
    parser.add_argument("card", type=Path)
    args = parser.parse_args()
    embed(args.snake, args.card)
