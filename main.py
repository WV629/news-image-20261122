# news-image-20261122 — "The World in One Day"
# Entrypoint: copies the committed entry.png to the output directory
# the harness expects (MAKEFUN_OUTPUT_DIR, or /output as a fallback).
# Python 3.13, standard library only, no network, fully deterministic:
# the same bytes go in, the same bytes come out, every run.
#
# The image is a one-page newspaper front page summing up Sunday
# 22 November 2026 in 36 stories: a headline stat strip, 3 drawn
# feature stories, 10 smaller stories, a world map with numbered
# pins, 23 more briefs, a markets strip, and a DATE CHECK box that
# names the big Thursday 19 and Friday 20 Nov stories and keeps them
# out of the Sunday paper. COP31's second day of overtime leads,
# with the Riyadh alert, the Sinaloa "Chapo Isidro" raid, the Nvidia
# SEC probe, Bitcoin's two-year low and rebound, Trump's 10% card-rate
# cap vow, France's sixth protest weekend and the ATP Finals final.
# It was drawn in code (see generate.py) and committed here as entry.png.

import os
import shutil
import sys

# Resolve the directory this file lives in, so the copy works no
# matter which working directory the harness runs us from.
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")

# The harness sets MAKEFUN_OUTPUT_DIR; /output is the documented
# fallback when it is not set. An empty or whitespace-only value
# counts as unset, so a stray blank env var cannot send the image
# to a relative or empty path.
OUT_DIR = (os.environ.get("MAKEFUN_OUTPUT_DIR") or "").strip() or "/output"
TARGET = os.path.join(OUT_DIR, "entry.png")


def main():
    if not os.path.isfile(SOURCE):
        print("entry image missing: %s" % SOURCE, file=sys.stderr)
        return 1
    with open(SOURCE, "rb") as fh:
        magic = fh.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        print("entry image is not a PNG: %s" % SOURCE, file=sys.stderr)
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    if os.path.getsize(TARGET) != os.path.getsize(SOURCE):
        print("copy size mismatch: %s" % TARGET, file=sys.stderr)
        return 1
    print("news-image-20261122: copied entry.png (%s) -> %s" % (SOURCE, TARGET))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
