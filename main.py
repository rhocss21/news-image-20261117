"""Copy the pre-rendered front page to the grader's output directory.

The image is rendered offline by draw.py (Pillow) and shipped beside this
file as entry.png; this program needs only the standard library, runs with
no network, and writes identical bytes on every run. Before copying it
checks the file is a whole PNG inside the competition's 1 MiB gate, so a
truncated render fails loudly instead of submitting a broken image.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576


def main():
    src = os.path.join(HERE, "entry.png")
    with open(src, "rb") as fh:
        head = fh.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        raise SystemExit("entry.png is not a PNG file")
    if os.path.getsize(src) > MAX_BYTES:
        raise SystemExit("entry.png exceeds the 1 MiB gate")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
