#!/usr/bin/env python3
"""
OCR detection script using EasyOCR.
Detects text in images and returns results with bounding box coordinates.

Usage:
    python3 ocr_detect.py --input photo.jpg
    python3 ocr_detect.py --input photo.jpg --pattern "\\d{4}"
    python3 ocr_detect.py --input photo.jpg --match "9347,0295"

Output (JSON to stdout):
    [
      {"text": "9347", "bbox": [x1, y1, x2, y2], "confidence": 0.95},
      ...
    ]
"""

import argparse
import json
import re
import sys
import os

os.environ.setdefault("EASYOCR_MODULE_PATH", os.path.expanduser("~/.EasyOCR"))


def detect(input_path, pattern=None, match_codes=None, langs=None):
    """Run OCR on an image and return detections with bounding boxes."""
    try:
        import easyocr
    except ImportError:
        print("ERROR: easyocr is required. Install with: pip3 install easyocr", file=sys.stderr)
        sys.exit(1)

    if langs is None:
        langs = ["ch_sim", "en"]

    reader = easyocr.Reader(langs, gpu=False, verbose=False)
    raw_results = reader.readtext(input_path)

    detections = []
    for (corners, text, confidence) in raw_results:
        # EasyOCR returns 4 corners: [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
        # Convert to [x1, y1, x2, y2] bounding box
        xs = [int(c[0]) for c in corners]
        ys = [int(c[1]) for c in corners]
        bbox = [min(xs), min(ys), max(xs), max(ys)]

        text = text.strip()
        if not text:
            continue

        detections.append({
            "text": text,
            "bbox": bbox,
            "confidence": round(confidence, 4),
        })

    # Filter by regex pattern if provided
    if pattern:
        regex = re.compile(pattern)
        detections = [d for d in detections if regex.search(d["text"])]

    # Filter by match codes if provided
    if match_codes:
        codes = set(match_codes)
        matched = []
        for d in detections:
            for code in codes:
                if code in d["text"] or d["text"] in code:
                    d["matched_code"] = code
                    matched.append(d)
                    break
        detections = matched

    return detections


def main():
    parser = argparse.ArgumentParser(description="OCR detection with bounding boxes")
    parser.add_argument("--input", "-i", required=True, help="Input image path")
    parser.add_argument("--pattern", "-p", default=None,
                        help="Regex pattern to filter results (e.g., '\\d{4}')")
    parser.add_argument("--match", "-m", default=None,
                        help="Comma-separated pickup codes to match against")
    parser.add_argument("--langs", default="ch_sim,en",
                        help="Comma-separated language codes (default: ch_sim,en)")
    parser.add_argument("--output", "-o", default=None,
                        help="Write JSON to file instead of stdout")

    args = parser.parse_args()

    langs = [l.strip() for l in args.langs.split(",")]
    match_codes = [c.strip() for c in args.match.split(",")] if args.match else None

    detections = detect(args.input, pattern=args.pattern, match_codes=match_codes, langs=langs)

    result_json = json.dumps(detections, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result_json)
        print(f"Detections saved to: {args.output}", file=sys.stderr)
    else:
        print(result_json)


if __name__ == "__main__":
    main()
