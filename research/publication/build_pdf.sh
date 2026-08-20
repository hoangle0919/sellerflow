#!/usr/bin/env bash
# Builds MANUSCRIPT.pdf from MANUSCRIPT.md.
#
# Three stages, because two problems cannot be solved from the markdown alone:
#
#   1. pandoc -> LaTeX. The markdown carries its own H1 and author lines so it
#      reads correctly standalone; for the PDF those are stripped and replaced
#      by a raw LaTeX title block passed via --include-before-body, which the
#      template emits ahead of the table of contents.
#
#      +autolink_bare_uris matters: without it every reference URL is plain
#      text, which TeX cannot break, and the References pages overflow.
#
#   2. fix_tex.py. Adds break opportunities inside artifact paths and SHA-256
#      digests, and fills in the PDF Title/Author properties that pandoc leaves
#      empty for a document with no title block. Adds no glyphs.
#
#   3. xelatex, three passes -- TOC page numbers settle on the second, and
#      longtable column widths on the third.
#
# Nothing transforms content. If a number changes in the manuscript it changes
# in the PDF; there is no separate figure source.
#
# Verify afterwards with:  python3 check_pdf_bounds.py MANUSCRIPT.pdf
#
# Usage:  ./build_pdf.sh          (from research/publication/)
# Requires: pandoc, xelatex, DejaVu fonts, xurl.sty, python3.
#
# Then gate the result:  python3 check_pdf_bounds.py MANUSCRIPT.pdf
# That script needs PyMuPDF (`pip install pymupdf`), which this one does not.

set -euo pipefail
cd "$(dirname "$0")"

SRC="MANUSCRIPT.md"
OUT="MANUSCRIPT.pdf"
WORK="$(mktemp -d /tmp/manuscript_build_XXXX)"
trap 'rm -rf "$WORK"' EXIT

cat > "$WORK/head.tex" <<'TITLEBLOCK'
\begin{center}
{\LARGE\bfseries Revenue-Contingent Financing Under Volatile Sales}\\[7pt]
{\large Separating Price from Structure in a Paired Simulation Study}\\[16pt]
{\large Le Huu Hoang}\\[4pt]
{\small Independent research \textperiodcentered{} August 2026}\\[3pt]
{\small \href{mailto:lehuuhoang1909@gmail.com}{lehuuhoang1909@gmail.com} \textperiodcentered{} \url{https://sellerflow-production.up.railway.app}}
\end{center}
\vspace{14pt}
TITLEBLOCK

# Drop the markdown H1 and the three author lines that follow it; keep the rest.
awk 'NR==1 && /^# / {next}
     NR<=6 && /^\*\*Le Huu Hoang\*\*/ {next}
     NR<=6 && /^Independent research/ {next}
     NR<=6 && /^lehuuhoang/ {next}
     {print}' "$SRC" > "$WORK/body.md"

pandoc "$WORK/body.md" -s -t latex -o "$WORK/raw.tex" \
  -f markdown+autolink_bare_uris \
  --include-before-body="$WORK/head.tex" \
  -V documentclass=article \
  -V papersize=a4 \
  -V geometry:margin=2.4cm \
  -V mainfont="DejaVu Serif" \
  -V sansfont="DejaVu Sans" \
  -V monofont="DejaVu Sans Mono" \
  -V fontsize=10pt \
  -V colorlinks=true -V linkcolor=RoyalBlue -V urlcolor=RoyalBlue \
  --toc --toc-depth=2 \
  --highlight-style=tango

python3 fix_tex.py "$WORK/raw.tex" "$WORK/manuscript.tex"

for pass in 1 2 3; do
  (cd "$WORK" && xelatex -interaction=nonstopmode -halt-on-error manuscript.tex) \
    > "$WORK/pass$pass.log" 2>&1 || {
      echo "xelatex failed on pass $pass:"; tail -30 "$WORK/pass$pass.log"; exit 1; }
done

overfull=$(grep -c "Overfull \\\\hbox" "$WORK/pass3.log" || true)
cp "$WORK/manuscript.pdf" "$OUT"
echo "Built $OUT ($(pdfinfo "$OUT" | awk '/^Pages/{print $2}') pages, ${overfull} overfull hbox warnings)"
