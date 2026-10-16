#!/usr/bin/env python3
"""Repo integrity gate for CI.

Checks the invariants this repo is built on:

  * media blobs are never committed (masters live off-repo)
  * no tracked file exceeds GitHub's 100 MB file limit
  * every *SHA256SUMS manifest is well-formed
  * the season has 15 artists and every artist has one fine print with a genre
  * the documented doc mirrors are byte-identical
  * every tracked Python / shell / JSON file parses
  * (with --site) every relative link in the built site resolves

Usage:  python3 tools/ci_check.py [--site _site]
"""
import argparse, glob, hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems = []
def fail(msg):
    problems.append(msg)
    print(f"FAIL  {msg}")

def tracked():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True, text=True).stdout
    return [p for p in out.split("\0") if p]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

MEDIA_EXT = {".wav", ".aiff", ".aif", ".aifc", ".flac", ".mp3", ".m4a", ".aac", ".ogg", ".opus",
             ".mov", ".mp4", ".m4v", ".mkv", ".avi", ".webm", ".prproj"}
MAX_BYTES = 100 * 1024 * 1024

def check_hygiene(files):
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in MEDIA_EXT:
            fail(f"media blob tracked: {f}")
        if os.path.basename(f).startswith("._") or os.path.basename(f) == ".DS_Store":
            fail(f"AppleDouble/DS_Store tracked: {f}")
        p = os.path.join(ROOT, f)
        if os.path.isfile(p) and os.path.getsize(p) > MAX_BYTES:
            fail(f"tracked file exceeds 100 MB: {f}")

MANIFEST_LINE = re.compile(r"^[0-9a-f]{64}  .+$")
def check_manifests(files):
    n = 0
    for f in files:
        if not f.endswith("SHA256SUMS"):
            continue
        n += 1
        bad = 0
        for i, line in enumerate(open(os.path.join(ROOT, f), encoding="utf-8", errors="replace"), 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if not MANIFEST_LINE.match(s):
                bad += 1
                if bad <= 3:
                    fail(f"{f}:{i}: malformed manifest line: {s[:80]}")
        if bad > 3:
            fail(f"{f}: {bad} malformed lines total")
    print(f"  checked {n} SHA256SUMS manifests")

def check_artists():
    base = os.path.join(ROOT, "Season One", "Artists")
    artists = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))
    if len(artists) != 15:
        fail(f"expected 15 artists, found {len(artists)}: {artists}")
    for a in artists:
        press = os.path.join(base, a, "Press")
        if not os.path.isdir(press):
            fail(f"{a}: no Press/ directory"); continue
        fine = [f for f in os.listdir(press) if f.startswith("FINE_PRINT_") and f.endswith(".md")]
        if len(fine) != 1:
            fail(f"{a}: expected 1 FINE_PRINT_*.md, found {fine}"); continue
        text = open(os.path.join(press, fine[0]), encoding="utf-8", errors="replace").read()
        if not re.search(r"\*\*Style\s*/\s*genres?:\*\*", text, re.I):
            fail(f"{a}: {fine[0]} has no 'Style / genres:' line")
    print(f"  checked {len(artists)} artists")

MIRRORS = [
    ("qc/SeasonOne_Mix_qc.md", "Season One/QC/SeasonOne_Mix_qc.md"),
    ("qc/SeasonOne_EPK_qc.md", "Season One/QC/SeasonOne_EPK_qc.md"),
    ("qc/SeasonOne_Release_Checklist.md", "Season One/QC/SeasonOne_Release_Checklist.md"),
    ("qc/SeasonOne_EPK_SHA256SUMS", "Season One/QC/SeasonOne_EPK_SHA256SUMS"),
    ("MASTER_README.md", "Season One/Docs/MASTER_README.md"),
    ("BRAND_GUIDELINES.md", "Season One/Docs/BRAND_GUIDELINES.md"),
    ("EPK_Audio_Workflow.md", "Season One/Docs/EPK_Audio_Workflow.md"),
    ("epk_lab_promotion.md", "Season One/Docs/epk_lab_promotion.md"),
]
def check_mirrors():
    for a, b in MIRRORS:
        pa, pb = os.path.join(ROOT, a), os.path.join(ROOT, b)
        if not (os.path.isfile(pa) and os.path.isfile(pb)):
            fail(f"mirror missing: {a} / {b}"); continue
        if sha256(pa) != sha256(pb):
            fail(f"mirror drift: {a} != {b}")
    print(f"  checked {len(MIRRORS)} doc mirrors")

def check_syntax(files):
    import py_compile
    from tempfile import mkdtemp
    tmp = mkdtemp()
    for f in files:
        if f.endswith(".py"):
            try:
                py_compile.compile(os.path.join(ROOT, f), cfile=os.path.join(tmp, "x.pyc"), doraise=True)
            except py_compile.PyCompileError as e:
                fail(f"python syntax: {f}: {str(e).splitlines()[0]}")
        elif f.endswith(".sh"):
            r = subprocess.run(["bash", "-n", os.path.join(ROOT, f)], capture_output=True, text=True)
            if r.returncode:
                fail(f"shell syntax: {f}: {r.stderr.strip().splitlines()[0] if r.stderr else ''}")
        elif f.endswith(".json"):
            try:
                json.load(open(os.path.join(ROOT, f), encoding="utf-8"))
            except (ValueError, OSError) as e:
                fail(f"json: {f}: {e}")
    print("  checked python / shell / json syntax")

ATTR = re.compile(r'(?:href|src)="([^"]*)"')
def check_links(site):
    if not os.path.isdir(site):
        fail(f"site directory not found: {site}"); return
    pages = glob.glob(os.path.join(site, "**", "*.html"), recursive=True)
    missing = 0
    for pg in pages:
        base = os.path.dirname(pg)
        for url in ATTR.findall(open(pg, encoding="utf-8", errors="replace").read()):
            if re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*:|#|//)", url):
                continue
            path = url.split("#", 1)[0].split("?", 1)[0]
            if not path:
                continue
            target = os.path.normpath(os.path.join(base, path))
            if os.path.isfile(target) or os.path.isfile(os.path.join(target, "index.html")):
                continue
            missing += 1
            if missing <= 10:
                fail(f"{os.path.relpath(pg, site)}: broken link -> {url}")
    if missing > 10:
        fail(f"{missing} broken links total")
    print(f"  checked {len(pages)} site pages, {missing} broken links")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=None, help="built site dir to link-check")
    args = ap.parse_args()
    files = tracked()
    print(f"ci_check: {len(files)} tracked files")
    check_hygiene(files)
    check_manifests(files)
    check_artists()
    check_mirrors()
    check_syntax(files)
    if args.site:
        check_links(args.site)
    print()
    if problems:
        print(f"ci_check: {len(problems)} problem(s)")
        return 1
    print("ci_check: all checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
