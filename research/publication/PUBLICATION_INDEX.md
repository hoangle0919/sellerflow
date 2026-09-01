# Publication Index

**Which document to read, and which to cite.** This index is authoritative for document status. If any other file disagrees about which paper is current, this one is right and the disagreement is a defect to be logged.

Last reconciled: 2026-08-27.

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
| `reader_editions/SHA256SUMS.handoff.txt` | Identities as received, for transfer verification |

Both builders verify four registered artifact checksums before rendering and abort on mismatch. Build instructions are in the supplement, §4.2.

---

## Historical — retained, never cited as current

| Document | Status | Why retained |
|---|---|---|
| [`MANUSCRIPT.md`](MANUSCRIPT.md) / [`MANUSCRIPT.pdf`](MANUSCRIPT.pdf) | **Historical technical manuscript**, 19 pages | The full-apparatus version: per-claim source notes, checksum tables, the reproducibility statement. Superseded as the public paper; it is the raw material the supplement was harvested from, and the record of how the argument was assembled. Preserved byte-for-byte. |
| [`TONG_QUAN_VI.md`](TONG_QUAN_VI.md) / [`TONG_QUAN_VI.pdf`](TONG_QUAN_VI.pdf) | **Superseded Vietnamese overview**, 5 pages | A short summary written before the Vietnamese scholarly edition existed. Superseded by the 14-page Vietnamese paper. Retained as dated history; not the Vietnamese academic paper. |

Neither is deleted and neither is overwritten. Figures were shown from them, so the record of what was said and when has to stay checkable. Document identities are listed in the supplement, §1.

---

## Supporting documents

| Path | Role |
|---|---|
| `LITERATURE_MATRIX.md` | 44 verified sources, 6 documented evidence gaps, with what each source does **not** support |
| `PAPER_OUTLINE.md` | Every figure bound to a ledger ID and artifact path |
| `CAREER_PACKAGE.md` | Résumé, portfolio and interview text, with a "what must never be said" table |
| `../CLAIM_LEDGER.md` | Every claim cleared for public use, with its artifact and required qualifier |
| `../DECISION_LOG.md` | D-001 … D-055, append-only, including every retraction |
| `../METHODOLOGY_SPEC.md` | The frozen specification, v1.0 + amendments A-1…A-9 |
| `../RESULTS_REGISTRY.md` | R-000 … R-014, each with a public-safety classification |

---

## The fourth artifact

**SellerFlow** — https://sellerflow-production.up.railway.app — is the live research prototype demonstrating the financing mechanism. It is a **demonstration**: it holds no capital, makes no credit decisions, and as of August 2026 has used no external merchant data. It is not part of the publication set and carries no research finding; the Simulation Lab within it reads the same registered artifacts the papers do.

---

## If you only read one thing

- **To evaluate the argument** → the English paper, 14 pages.
- **To check whether the numbers are real** → the supplement, §2 and §4.
- **To see what was got wrong and corrected** → the supplement, §6, then `DECISION_LOG.md`.
