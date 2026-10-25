#!/usr/bin/env python3
"""Catalogue parity and key-coverage check.

Three failures this catches, each of which a grep would miss:

  1. A key present in one catalogue and absent from the other. The runtime
     falls back to English rather than rendering a raw key at a reader, which
     is the right behaviour at runtime and exactly what makes the gap invisible
     in a browser. It has to fail here instead.
  2. A key referenced in markup or script that exists in no catalogue.
  3. A Vietnamese value byte-identical to its English one. Sometimes correct
     (proper names, "VND + ≈ USD"), so these are listed as warnings and
     allowlisted explicitly rather than failed blindly.

Exit status is non-zero on a real failure, so this is usable in CI.
"""
from __future__ import annotations
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "frontend", "i18n")

#: Values that legitimately read the same in both catalogues.
IDENTICAL_OK = {
    "lang.en", "lang.vi", "chrome.menu",
    "fx.display.dual", "fx.approx",
    "research.paper.vi",
    "demo.key.headerSuffix",   # "header." -- the HTTP term, not translated
    "lab.prov.col.sha",       # "SHA-256" -- an algorithm name, not prose
}

SCAN_GLOBS = [
    ("frontend", (".html", ".js")),
    ("backend", (".py",)),
]
KEY_RE = re.compile(r'data-i18n(?:-html)?="([^"]+)"')
ATTR_RE = re.compile(r'data-i18n-attr="([^"]+)"')
CALL_RE = re.compile(r"""(?:RBF_I18N\.t|\bt)\(\s*['"]([a-z][a-zA-Z0-9_.]*\.[a-zA-Z0-9_.]+)['"]""")

#: Keys are not only passed directly to t(). They also sit in lookup tables and
#: arrays -- VERDICT, CHIP_DEFS, DECISION_STEPS -- and are dereferenced later.
#: A call-site regex cannot see those, and the consequence is worse than a
#: missing translation: t() returns '' for an unknown key, so the label renders
#: BLANK in every language, English included. 85 such keys were live when this
#: was added. Any string literal under a known namespace is therefore treated
#: as a reference.
LITERAL_RE = re.compile(
    r"""['"]((?:demo|lab|labpage|chrome|fx|lang|footer|meta|hero|figure|scope|"""
    r"""approach|research|status|questions|contact)\.[a-zA-Z0-9_.]+)['"]""")


def load(lang):
    with open(os.path.join(CAT, f"{lang}.json"), encoding="utf-8") as f:
        return json.load(f)


def referenced_keys():
    found = set()
    for sub, exts in SCAN_GLOBS:
        base = os.path.join(ROOT, sub)
        for dirpath, _dirs, files in os.walk(base):
            if "i18n" in dirpath.split(os.sep) or "__pycache__" in dirpath:
                continue
            for fn in files:
                if not fn.endswith(exts):
                    continue
                # The runtime documents the markup contract in its own header
                # comment ("aria-label:key|title:k"), which the attribute regex
                # would otherwise read as two real key references.
                if fn == "i18n.js":
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    src = open(p, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                found |= set(KEY_RE.findall(src))
                found |= set(CALL_RE.findall(src))
                found |= set(LITERAL_RE.findall(src))
                for m in ATTR_RE.findall(src):
                    for pair in m.split("|"):
                        if ":" in pair:
                            found.add(pair.split(":", 1)[1].strip())
    return found


def main():
    en, vi = load("en"), load("vi")
    failures, warnings = [], []

    only_en = sorted(set(en) - set(vi))
    only_vi = sorted(set(vi) - set(en))
    if only_en:
        failures.append(f"{len(only_en)} key(s) in en.json missing from vi.json: {only_en[:8]}")
    if only_vi:
        failures.append(f"{len(only_vi)} key(s) in vi.json missing from en.json: {only_vi[:8]}")

    used = referenced_keys()
    # A literal ending in "." is a concatenation prefix (e.g. "lab.cls." + value),
    # not a key. Treat it as such rather than reporting a phantom miss.
    used = {k for k in used if not k.endswith(".")}
    # ...and a literal whose last segment is a file extension is a filename
    # ("demo.html", "lab.py"), not a catalogue key.
    used = {k for k in used if k.rsplit(".", 1)[-1] not in
            {"html", "py", "js", "json", "css", "md", "csv", "svg", "txt"}}
    undefined = sorted(k for k in used if k not in en and k not in vi)
    if undefined:
        failures.append(f"{len(undefined)} referenced key(s) defined in no catalogue: {undefined[:8]}")

    for k in sorted(set(en) & set(vi)):
        if k not in IDENTICAL_OK and en[k] == vi[k]:
            warnings.append(k)

    unused = sorted(set(en) - used)

    print(f"en={len(en)} vi={len(vi)} referenced={len(used)}")
    if warnings:
        print(f"\nWARN · {len(warnings)} Vietnamese value(s) identical to English "
              f"(add to IDENTICAL_OK if intended):")
        for k in warnings[:20]:
            print(f"    {k}")
    if unused:
        print(f"\nnote · {len(unused)} catalogue key(s) not referenced in scanned sources "
              f"(expected for keys used only by pages not yet converted):")
        for k in unused[:20]:
            print(f"    {k}")
    if failures:
        print("\nFAIL")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("\nOK — catalogues are in parity and every referenced key resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
