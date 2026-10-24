# Publication Index

**Which document to read, and which to cite.** This index is authoritative for document status. If any other file disagrees about which paper is current, this one is right and the disagreement is a defect to be logged.

Last reconciled: 2026-10-24 (author-requested declaration correction; scientific results unchanged).

---

## Current — cite these

| Document | Language | Pages | Reader |
|---|---|---|---|
| [`reader_editions/papers/Revenue_Contingent_Financing_Professional_Paper.pdf`](reader_editions/papers/Revenue_Contingent_Financing_Professional_Paper.pdf) | English | 14, Letter | Reviewers, academic and international readers, hiring |
| [`reader_editions/papers/Tai_Tro_Hoan_Tra_Theo_Doanh_Thu_Bai_Nghien_Cuu.pdf`](reader_editions/papers/Tai_Tro_Hoan_Tra_Theo_Doanh_Thu_Bai_Nghien_Cuu.pdf) | Vietnamese | 14, Letter | Vietnamese academic and industry readers |
| [`REPRODUCIBILITY_SUPPLEMENT.md`](REPRODUCIBILITY_SUPPLEMENT.md) | English | — | Anyone verifying the work |

The two papers are **parallel in status and in claim boundaries, and independent in prose**. The Vietnamese edition is a Vietnamese scholarly paper in its own right, not a sentence-by-sentence translation. Neither is a translation of the other; both carry the same JEL classification (G23, G32, C63, O16, L81) and the same qualifications.

The supplement is a **companion, not an appendix**. The papers carry the argument; the supplement carries checksums, JSON paths, reproduction commands, tested environments and the correction record. They were separated deliberately — merging them produced a document that read like an engineering audit and buried the qualifications a reader most needs.

### Sources and builders

| Path | Role |
|---|---|
| `reader_editions/academic_paper_template.html` | Editable English source |
| `reader_editions/academic_paper_vi_template.html` | Editable Vietnamese source |
| `reader_editions/build_professional_paper.py` | English builder |
| `reader_editions/build_professional_paper_vi.py` | Vietnamese builder |
| `reader_editions/requirements-publication.txt` | Pinned publication dependencies |
| `reader_editions/SHA256SUMS.txt` | **Runnable manifest.** Exactly seven checksum records, no comments — so both checkers parse it without warnings. Verify from `research/publication/reader_editions/`: macOS `shasum -a 256 -c SHA256SUMS.txt`; GNU/Linux `sha256sum -c SHA256SUMS.txt` |
| `reader_editions/SHA256SUMS.handoff.txt` | **Archival transfer receipt.** Identities as they arrived in the incoming ZIP, whose layout differs from the repository's. Not runnable from its committed location, by design |

Both builders verify four registered artifact checksums before rendering and abort on mismatch. Build instructions are in the supplement, §4.2.

**Publication-only revision, 2026-10-24.** The author requested a simpler declaration while retaining the statements of no external funding and no financial interest in an RBF provider. Both reader editions and the historical technical manuscript were rebuilt. Reader editions remain 14 Letter pages; the historical manuscript remains 19 A4 pages. Numerical findings, citations and registered research artifacts were not revised. Current document identities are in the supplement and runnable manifest; earlier binaries remain in Git history.

---

## Historical — retained, never cited as current

| Document | Status | Why retained |
|---|---|---|
| [`MANUSCRIPT.md`](MANUSCRIPT.md) / [`MANUSCRIPT.pdf`](MANUSCRIPT.pdf) | **Historical technical manuscript**, 19 pages | The full-apparatus version: per-claim source notes, checksum tables, the reproducibility statement. Superseded as the public paper; its apparatus supplied the supplement. Rebuilt on 2026-10-24 only for the author-requested declaration correction; scientific content is unchanged. The Markdown also carries status framing excluded from the PDF body. Earlier versions remain in Git history. |
| [`TONG_QUAN_VI.md`](TONG_QUAN_VI.md) / [`TONG_QUAN_VI.pdf`](TONG_QUAN_VI.pdf) | **Superseded Vietnamese overview**, 5 pages | A short summary written before the Vietnamese scholarly edition existed. Superseded by the 14-page Vietnamese paper. Retained as dated history; not the Vietnamese academic paper. |

**Exactly what is preserved, and what is not.** State these three separately, because collapsing them overstates the guarantee:

1. **Three PDF identities changed on 2026-10-24.** Both reader editions and `MANUSCRIPT.pdf` were rebuilt for the author-requested declaration correction. `TONG_QUAN_VI.pdf` is unchanged. Previous PDF identities remain recorded in Git history and the archival handoff receipt, not asserted as current.
2. **The historical Markdown sources carry status framing.** Their banners and current-edition pointers are separate from the PDF bodies. The manuscript declaration also carries the 2026-10-24 correction; the Markdown/PDF pairs are not jointly byte-identical.
3. **Scientific content was not revised.** No argument, numerical result, figure, table or citation was changed by the declaration correction. Existing historical corrections and qualifications remain visible; the current papers and supplement govern present claims.

Neither file is deleted. Figures were published from them, so the record of what was said and when has to stay checkable. Document identities are in the supplement, §1.

---

## Supporting documents

| Path | Role |
|---|---|
| `LITERATURE_MATRIX.md` | 44 verified sources, 6 documented evidence gaps, with what each source does **not** support |
| `PAPER_OUTLINE.md` | Every figure bound to a ledger ID and artifact path |
| `CAREER_PACKAGE.md` | Résumé, portfolio and interview text, with a "what must never be said" table |
| `../CLAIM_LEDGER.md` | Every claim cleared for public use, with its artifact and required qualifier |
| `../DECISION_LOG.md` | Append-only, including every retraction. Coverage is **D-001–D-045 and D-047–D-057**. **No `## D-046` entry was ever written**, although the identifier was used: D-047 cites D-046 as if it existed. The missing record is documented in **D-057**; neither D-047 nor D-056 is rewritten, because a dated entry edited after the fact cannot be audited |
| `../METHODOLOGY_SPEC.md` | The frozen specification, v1.0 + amendments A-1…A-9 |
| `../RESULTS_REGISTRY.md` | R-000 … R-014, each with a public-safety classification |

---

## The fourth artifact

**SellerFlow** — https://sellerflow-production.up.railway.app — is the live research prototype demonstrating the financing mechanism. It is a **demonstration**: it holds no capital, makes no credit decisions, and as of August 2026 has used no external merchant data. It is not part of the publication set and carries no research finding; the Simulation Lab within it reads the same registered artifacts the papers do.

---

## If you only read one thing

- **To evaluate the argument** → the **English paper** (14 pages), or the **Vietnamese edition** if Vietnamese is your reading language — they are parallel in status, not one derived from the other.
- **To check whether the numbers are real** → the supplement, §2 and §4.
- **To see what was got wrong and corrected** → the supplement, §6, then `DECISION_LOG.md`.
