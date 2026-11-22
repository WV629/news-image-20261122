#!/usr/bin/env python3
"""Entrypoint for news-image-20261122: copy entry.png into the
directory the make.fun harness gives us (MAKEFUN_OUTPUT_DIR),
defaulting to /output. The picture itself is rendered by
generate.py; this file only moves the finished file. The harness
limits entrypoints to the Python standard library, so this file
imports nothing beyond it.
"""
import os
import shutil
from pathlib import Path


def entrypoint():
    here = Path(__file__).resolve().parent
    src = here / "entry.png"
    if not src.is_file():
        raise SystemExit("entry.png missing: run generate.py first")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)
    print("entry.png -> %s (%d bytes)" % (dst, dst.stat().st_size))


if __name__ == "__main__":
    entrypoint()
