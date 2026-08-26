#!/usr/bin/env python3
"""Post-process pandoc's LaTeX so long literals can break across lines.

The manuscript is dense with artifact filenames, JSON paths and SHA-256
digests. TeX treats each as a single unbreakable word, so they ran off the
page edge -- on pages 2, 5, 10, 14 and 15 the overflow was clipping the very
identifiers a reader would need in order to check a figure.

Nothing here alters content. `\\allowbreak` is a break *opportunity*: it emits
no glyph, so the extracted text is byte-identical to the input. A digest may
now wrap across two lines, but the same 64 characters are present, in order.

Also fills in the PDF Title and Author metadata, which pandoc leaves empty
when the document has no title block.

Usage: python3 fix_tex.py in.tex out.tex
"""
import re
import sys

TITLE = ("Revenue-Contingent Financing Under Volatile Sales: "
         "Separating Price from Structure in a Paired Simulation Study")
AUTHOR = "Le Huu Hoang"
SUBJECT = ("Paired simulation study of revenue-contingent versus "
           "cost-matched fixed-instalment small-business financing")
KEYWORDS = ("revenue-based financing; revenue-contingent repayment; "
            "merchant cash advance; payment burden; provider recovery; "
            "paired simulation; factor rate; APR")

HEX_RUN = re.compile(r"^[0-9a-f]{32,}$")


def _spans(tex, macro):
    """Yield (start, end, inner) for each top-level \\macro{...}, brace-matched."""
    needle = "\\" + macro + "{"
    i = 0
    while True:
        i = tex.find(needle, i)
        if i == -1:
            return
        j = i + len(needle)
        depth, k = 1, j
        while k < len(tex) and depth:
            c = tex[k]
            if c == "\\":
                k += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            k += 1
        yield i, k, tex[j:k - 1]
        i = k


def breakable(inner: str) -> str:
    """Insert break opportunities into one \\texttt{} payload."""
    # A bare digest has no separator to break at, so chunk it.
    plain = inner.replace("\\_", "_")
    if HEX_RUN.match(plain):
        return "\\allowbreak{}".join(
            inner[n:n + 8] for n in range(0, len(inner), 8))

    out, i = [], 0
    while i < len(inner):
        if inner.startswith("\\_", i):          # escaped underscore
            out.append("\\_\\allowbreak{}")
            i += 2
        elif inner[i] in "/.":                   # path and dot breaks only
            # NOT "-". A break after a hyphen renders correctly on the page but
            # copies out with the hyphen missing: PDF text extractors treat a
            # trailing hyphen as line-end hyphenation and de-hyphenate when
            # rejoining. §2b already avoids this in URLs; it was still live for
            # inline code, where it silently corrupted a NUMBER —
            # `5.351e-15` extracted as `5.351e15`, thirty orders of magnitude
            # out, in a reproducibility claim. A period is safe because no
            # extractor de-periods.
            out.append(inner[i] + "\\allowbreak{}")
            i += 1
        elif inner[i] == "\\":                   # any other control sequence
            out.append(inner[i:i + 2])
            i += 2
        else:
            out.append(inner[i])
            i += 1
    return "".join(out)


def main(src: str, dst: str) -> None:
    tex = open(src, encoding="utf-8").read()

    # 1. Break opportunities inside inline code.
    edits = [(a, b, "\\texttt{" + breakable(inner) + "}")
             for a, b, inner in _spans(tex, "texttt")]
    for a, b, rep in reversed(edits):
        tex = tex[:a] + rep + tex[b:]

    # 2. PDF document properties. pandoc emits pdfcreator only when there is
    #    no title block, leaving Title and Author blank in the reader.
    meta = ("\\hypersetup{\n"
            f"  pdftitle={{{TITLE}}},\n"
            f"  pdfauthor={{{AUTHOR}}},\n"
            f"  pdfsubject={{{SUBJECT}}},\n"
            f"  pdfkeywords={{{KEYWORDS}}}}}\n")
    anchor = "\\urlstyle{same}"
    if anchor not in tex:
        raise SystemExit("fix_tex: expected \\urlstyle{same} anchor not found")

    # 2b. Do not break URLs at hyphens. url.sty emits the break as a
    #     discretionary hyphen, and PDF text extractors then de-hyphenate it --
    #     so the URL renders correctly on the page but copies out with a hyphen
    #     missing. Breaking only at structural characters avoids that, and also
    #     removes the reader's ambiguity about whether a hyphen at a line end
    #     belongs to the address. Verified against the page-edge check: this
    #     still yields zero overfull boxes.
    urlbreaks = (
        "\\makeatletter\n"
        "\\def\\UrlBreaks{\\do\\/\\do\\.\\do\\:\\do\\?\\do\\&\\do\\=\\do\\+"
        "\\do\\%\\do\\#\\do\\_\\do\\~\\do\\,\\do\\;\\do\\a\\do\\b\\do\\c\\do\\d"
        "\\do\\e\\do\\f\\do\\g\\do\\h\\do\\i\\do\\j\\do\\k\\do\\l\\do\\m\\do\\n"
        "\\do\\o\\do\\p\\do\\q\\do\\r\\do\\s\\do\\t\\do\\u\\do\\v\\do\\w\\do\\x"
        "\\do\\y\\do\\z\\do\\0\\do\\1\\do\\2\\do\\3\\do\\4\\do\\5\\do\\6\\do\\7"
        "\\do\\8\\do\\9}\n"
        "\\def\\UrlBigBreaks{\\do\\/\\do\\:}\n"
        "\\makeatother\n")
    tex = tex.replace(anchor, meta + anchor + "\n" + urlbreaks, 1)

    # 3. Let TeX work harder before it gives up and overflows.
    tex = tex.replace("\\setlength{\\emergencystretch}{3em}",
                      "\\setlength{\\emergencystretch}{3em}\n\\sloppy")

    open(dst, "w", encoding="utf-8").write(tex)
    print(f"fix_tex: {len(edits)} inline-code spans made breakable; "
          "PDF metadata set")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
