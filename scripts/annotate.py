#!/usr/bin/env python3
"""
Annotate an image with a red bounding box and optional label.
Used by the find-package skill to highlight matched packages on shelf photos.

Usage (manual boxes):
    python3 annotate.py --input photo.jpg --output result.jpg --box "x1,y1,x2,y2" --label "取件码: 5-2-1234"

Usage (from OCR detections):
    python3 annotate.py --input photo.jpg --output result.jpg --detections detections.json --match "9347"
"""

import argparse
import json
import sys
import os

def annotate(input_path, output_path, boxes, labels, line_width=None, font_size=None):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("ERROR: Pillow is required. Install with: pip3 install Pillow", file=sys.stderr)
        sys.exit(1)

    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)

    w, h = img.size
    if line_width is None:
        line_width = max(4, min(w, h) // 150)
    if font_size is None:
        font_size = max(20, min(w, h) // 30)

    # Try to load a font that supports Chinese characters
    font = None
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception:
                continue
    if font is None:
        try:
            font = ImageFont.truetype("Arial", font_size)
        except Exception:
            font = ImageFont.load_default()

    red = (255, 0, 0, 255)
    bg_color = (255, 0, 0, 180)
    text_color = (255, 255, 255, 255)

    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box

        # Draw thick red rectangle
        for offset in range(line_width):
            draw.rectangle(
                [x1 - offset, y1 - offset, x2 + offset, y2 + offset],
                outline=red
            )

        # Draw label if provided
        if i < len(labels) and labels[i]:
            label = labels[i]
            text_bbox = draw.textbbox((0, 0), label, font=font)
            tw = text_bbox[2] - text_bbox[0]
            th = text_bbox[3] - text_bbox[1]
            padding = 6

            # Position label above the box, or below if no room above
            lx = x1
            ly = y1 - th - padding * 2 - line_width
            if ly < 0:
                ly = y2 + line_width

            # Background rectangle for label
            draw.rectangle(
                [lx, ly, lx + tw + padding * 2, ly + th + padding * 2],
                fill=bg_color
            )
            draw.text((lx + padding, ly + padding), label, fill=text_color, font=font)

    # Save result
    if output_path.lower().endswith('.png'):
        img.save(output_path, 'PNG')
    else:
        img = img.convert('RGB')
        img.save(output_path, 'JPEG', quality=92)

    print(f"Annotated image saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Annotate image with red bounding boxes")
    parser.add_argument("--input", "-i", required=True, help="Input image path")
    parser.add_argument("--output", "-o", required=True, help="Output image path")
    parser.add_argument("--box", "-b", action="append", default=[],
                        help="Bounding box as 'x1,y1,x2,y2' (can specify multiple)")
    parser.add_argument("--label", "-l", action="append", default=[],
                        help="Label for each box (optional, can specify multiple)")
    parser.add_argument("--detections", "-d", default=None,
                        help="JSON file from ocr_detect.py (alternative to --box)")
    parser.add_argument("--match", "-m", default=None,
                        help="Comma-separated codes to match in detections")
    parser.add_argument("--line-width", type=int, default=None,
                        help="Line width in pixels (auto-scales if not set)")
    parser.add_argument("--font-size", type=int, default=None,
                        help="Font size in pixels (auto-scales if not set)")

    args = parser.parse_args()

    boxes = []
    labels = []

    if args.detections:
        # Load detections from OCR JSON
        with open(args.detections, "r", encoding="utf-8") as f:
            detections = json.load(f)

        if args.match:
            match_codes = [c.strip() for c in args.match.split(",")]
            for det in detections:
                for code in match_codes:
                    if code in det["text"] or det["text"] in code:
                        boxes.append(det["bbox"])
                        labels.append(f"取件码: {code}")
                        break
        else:
            # No match filter — annotate all detections
            for det in detections:
                boxes.append(det["bbox"])
                labels.append(det["text"])
    else:
        # Manual --box mode
        if not args.box:
            parser.error("Either --box or --detections is required")
        for b in args.box:
            coords = [int(c.strip()) for c in b.split(",")]
            if len(coords) != 4:
                print(f"ERROR: Box must have 4 coordinates, got: {b}", file=sys.stderr)
                sys.exit(1)
            boxes.append(coords)
        labels = args.label or []

    if not boxes:
        print("No matching detections found.", file=sys.stderr)
        sys.exit(1)

    annotate(args.input, args.output, boxes, labels,
             line_width=args.line_width, font_size=args.font_size)


if __name__ == "__main__":
    main()
