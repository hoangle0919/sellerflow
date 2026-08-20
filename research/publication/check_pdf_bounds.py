#!/usr/bin/env python3
"""Page-edge check for a generated PDF.

Fails if any text lies outside the intended text block. LaTeX reports overfull
hboxes to the log, but a log warning is easy to ignore and does not tell you
whether the overflow is cosmetic or whether it clipped a checksum. This
measures the rendered result instead.

Two thresholds:
  * MEDIA  -- text outside the page media box is unconditionally a failure;
              those glyphs cannot be read or copied at all.
  * MARGIN -- text intruding into the declared page margin is reported as a
              warning with the offending string, since a path or hash running
              into the margin is what a reader actually notices.

Requires PyMuPDF:  pip install pymupdf
    (imported as `pymupdf`; the older `fitz` alias is deprecated.) This is the
    only dependency the publication build adds beyond pandoc and xelatex, and
    it is not in backend/requirements.txt because nothing at runtime needs it.

Usage:  python3 check_pdf_bounds.py MANUSCRIPT.pdf [margin_cm]
Exit:   0 clean, 1 text outside the media box, 2 margin intrusions only.
"""
import sys

import pymupdf

PT_PER_CM = 28.3465
MEDIA_TOL = 0.75  # pt; glyph bbox rounding and font side bearings
# Hyphenated line-ends and hanging punctuation routinely sit a point or two
# past the measure because a glyph bounding box is wider than its advance
# width. Flagging those is noise, so the margin warning uses a looser bound.
MARGIN_TOL = 3.0


def check(path: str, margin_cm: float = 2.4):
    doc = pymupdf.open(path)
    margin = margin_cm * PT_PER_CM
    outside_media, in_margin = [], []

    for pno, page in enumerate(doc, start=1):
        media = page.rect
        text_l, text_r = media.x0 + margin, media.x1 - margin

        for x0, y0, x1, y1, word, *_ in page.get_text("words"):
            if x1 > media.x1 + MEDIA_TOL or x0 < media.x0 - MEDIA_TOL:
                outside_media.append((pno, word, round(x0, 1), round(x1, 1)))
            elif x1 > text_r + MARGIN_TOL:
                in_margin.append((pno, word, "right", round(x1 - text_r, 1)))
            elif x0 < text_l - MARGIN_TOL:
                in_margin.append((pno, word, "left", round(text_l - x0, 1)))
            if y1 > media.y1 + MEDIA_TOL or y0 < media.y0 - MEDIA_TOL:
                outside_media.append((pno, word, round(y0, 1), round(y1, 1)))

    print(f"{path}: {doc.page_count} pages, "
          f"media {doc[0].rect.width:.0f}x{doc[0].rect.height:.0f}pt, "
          f"margin {margin_cm}cm")

    if outside_media:
        print(f"\nFAIL -- {len(outside_media)} item(s) outside the media box:")
        for pno, word, a, b in outside_media[:40]:
            print(f"  p{pno:>3}  {a:>7} .. {b:>7}  {word[:70]}")
    else:
        print("\nPASS -- no text outside the media box.")

    if in_margin:
        print(f"\nWARN -- {len(in_margin)} item(s) intruding into the margin:")
        seen = set()
        for pno, word, side, over in in_margin:
            key = (pno, word, side)
            if key in seen:
                continue
            seen.add(key)
            print(f"  p{pno:>3}  {side:>5} +{over:>6}pt past text edge  {word[:70]}")
    else:
        print("WARN -- none. No text intrudes into the margin.")

    return 1 if outside_media else (2 if in_margin else 0)


if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else "MANUSCRIPT.pdf"
    cm = float(sys.argv[2]) if len(sys.argv) > 2 else 2.4
    sys.exit(check(pdf, cm))
