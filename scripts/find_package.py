#!/usr/bin/env python3
"""
One-stop script: OCR detect + match + annotate.

Usage:
    python3 find_package.py --input photo.jpg --code "9347" --output result.jpg
    python3 find_package.py --input photo.jpg --code "9347,0295" --output result.jpg

Outputs:
    - Annotated image at --output path
    - JSON result to stdout with match details
"""

import argparse
import json
import sys
import os

# Allow importing sibling modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_detect import detect
from annotate import annotate


def find_package(input_path, codes, output_path, langs=None):
    """Run OCR, match codes, annotate, and return results."""
    # Step 1: OCR detect all text
    all_detections = detect(input_path, langs=langs)

    # Step 2: Match against pickup codes
    codes_list = [c.strip() for c in codes.split(",")]
    matched = []
    unmatched = list(codes_list)

    for det in all_detections:
        for code in codes_list:
            if code in det["text"] or det["text"] in code:
                det["matched_code"] = code
                matched.append(det)
                if code in unmatched:
                    unmatched.remove(code)
                break

    # Step 3: Annotate if we have matches
    if matched:
        boxes = [m["bbox"] for m in matched]
        labels = [f"取件码: {m['matched_code']}" for m in matched]
        annotate(input_path, output_path, boxes, labels)

    return {
        "total_codes": len(codes_list),
        "found": len(matched),
        "not_found": len(unmatched),
        "matched": matched,
        "unmatched_codes": unmatched,
        "all_detections_count": len(all_detections),
        "output_image": output_path if matched else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Find packages by pickup code")
    parser.add_argument("--input", "-i", required=True, help="Shelf photo path")
    parser.add_argument("--code", "-c", required=True,
                        help="Pickup code(s) to find, comma-separated")
    parser.add_argument("--output", "-o", required=True, help="Annotated output path")
    parser.add_argument("--langs", default="ch_sim,en",
                        help="OCR languages (default: ch_sim,en)")

    args = parser.parse_args()
    langs = [l.strip() for l in args.langs.split(",")]

    result = find_package(args.input, args.code, args.output, langs=langs)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
