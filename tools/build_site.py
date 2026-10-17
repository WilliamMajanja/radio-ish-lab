#!/usr/bin/env python3
"""Build the Radio-ish Lab — Season One EPK microsite (static, GitHub Pages).

Everything is derived from tracked files: per-artist Press/FINE_PRINT_*.md and
Press/index.md, the EPK covers, and the top-level docs. Nothing is invented —
artists without a mirrored cover get a monogram placeholder, and genres are read
straight out of the fine print.

    python3 tools/build_site.py --out _site

Requires `markdown` (see tools/requirements.txt). Only relative intra-site links
are kept; every other relative link/image is rewritten to the GitHub repo so the
published site never has a dangling link.
"""
import argparse, html, os, re, shutil, sys, unicodedata

try:
    import markdown
except ImportError:  # pragma: no cover - the workflow installs requirements
    sys.exit("error: the 'markdown' package is required (pip install -r tools/requirements.txt)")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_URL = os.environ.get("RADIOISH_REPO_URL", "https://github.com/WilliamMajanja/radio-ish-lab")
BRANCH = os.environ.get("RADIOISH_BRANCH", "main")
SITE_NAME = "Radio-ish Lab"
SEASON = "Season One"
TAGLINE = "One house. Every sound."

# ── content map ──────────────────────────────────────────────────────────────
# (slug, nav title, page title, repo-relative source)
DOCS = [
    ("index", None, "Docs", None),
    ("readme", "Overview", "Project overview", "README.md"),
    ("master-readme", "Production index", "Production index", "MASTER_README.md"),
    ("season-one-readme", "Release standard", "Season One — release standard", "Season One/README.md"),
    ("brand-guidelines", "Brand", "Brand guidelines", "BRAND_GUIDELINES.md"),
    ("epk-audio-workflow", "Audio workflow", "EPK audio workflow", "EPK_Audio_Workflow.md"),
    ("epk-lab-promotion", "Label pitch", "The Lab — promotion", "epk_lab_promotion.md"),
    ("epk-project-index", "EPK project", "EPK project index", "EPK_Project/INDEX.md"),
    ("social-playbook", "Social", "Social playbook", "Social_Media/SOCIAL_PLAYBOOK.md"),
    ("media-kit", "Media kit", "Advertising media kit", "Advertising/MEDIA_KIT.md"),
    ("ad-creative", "Ad creative", "Advertising creative", "Advertising/AD_CREATIVE.md"),
    ("evidence", "Evidence", "QC evidence — overview", "qc/SeasonOne_Release_Checklist.md"),
    ("mix-qc", "Mix QC", "Mix QC report", "qc/SeasonOne_Mix_qc.md"),
    ("epk-qc", "EPK QC", "EPK QC report", "qc/SeasonOne_EPK_qc.md"),
    ("research-paper", "Research paper", "Season One — research paper", "RESEARCH_PAPER_SEASON_ONE.md"),
    ("migration", "Migration", "Catalogue migration record", "LAB_SESSION_1_PINET-ALPHA_MIGRATION.md"),
    ("license", "License", "License", "LICENSE"),
]
# docs shown in the header dropdown / docs index (skip the index sentinel)
NAV_DOCS = [d for d in DOCS if d[0] != "index"]

# ── helpers ──────────────────────────────────────────────────────────────────
def slugify(name):
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    n = re.sub(r"[^a-zA-Z0-9]+", "-", n).strip("-").lower()
    return n or "artist"

def esc(s):
    return html.escape(str(s), quote=True)

def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()

def render_md(text):
    md = markdown.Markdown(extensions=["extra", "sane_lists", "toc", "admonition"],
                           extension_configs={"toc": {"permalink": False}})
    return md.convert(text)

ATTR_RE = re.compile(r'(href|src)="([^"]*)"')

def rewrite_links(body, src_repo_path, doc_urls, site_path):
    """Point relative links at the rendered page when we have it, else GitHub."""
    src_dir = os.path.dirname(src_repo_path)

    def repl(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^([a-zA-Z][a-zA-Z0-9+.-]*:|#|//)", url):
            return m.group(0)
        anchor = ""
        if "#" in url:
            url, anchor = url.split("#", 1)
            anchor = "#" + anchor
        target = os.path.normpath(os.path.join(src_dir, url)) if url else src_dir
        for cand in (target, target + ".md", os.path.join(target, "index.md")):
            if cand in doc_urls:
                here = os.path.dirname(site_path)
                rel = os.path.relpath(doc_urls[cand], here or ".")
                return f'{attr}="{rel}{anchor}"'
        kind = "raw" if attr == "src" else "blob"
        return f'{attr}="{REPO_URL}/{kind}/{BRANCH}/{target}{anchor}"'

    return ATTR_RE.sub(repl, body)

# ── page chrome ──────────────────────────────────────────────────────────────
def page(title, body, depth=0, description=None):
    up = "../" * depth
    desc = description or f"{SITE_NAME} — {SEASON}: {TAGLINE}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {SITE_NAME}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)} · {SITE_NAME}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header class="site">
  <a class="brand" href="{up}index.html"><span class="dot" aria-hidden="true"></span>{SITE_NAME}</a>
  <nav>
    <a href="{up}index.html#roster">Roster</a>
    <a href="{up}evidence.html">Evidence</a>
    <a href="{up}docs/index.html">Docs</a>
    <a href="{REPO_URL}" rel="noopener">GitHub</a>
  </nav>
</header>
<main>
{body}
</main>
<footer class="site">
  <p><strong>{SITE_NAME}</strong> · {SEASON} · “{TAGLINE}”</p>
  <p>Created by <strong>William Majanja</strong> and <strong>DJ Bernie Cyber</strong> · Funded by <strong>B4 Hotel Management</strong></p>
  <p class="muted">Produced by Agent Mgumbe Studio · Developed by Schrödinger’s Breakfast (1nf1D3L [William Majanja])
     for Before Hotel Management (B4) · Executive Producer Bernie</p>
  <p class="muted"><a href="{REPO_URL}">Source &amp; evidence on GitHub</a> · © 2026 William Majanja</p>
</footer>
</body>
</html>
"""

CSS = """:root{--bg:#0e0e10;--panel:#151518;--line:#26262b;--fg:#f4f4f6;--mut:#9a9aa2;--max:1080px}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--fg);text-decoration:none;border-bottom:1px solid var(--line)}
a:hover{border-color:var(--fg)}
header.site{position:sticky;top:0;z-index:10;display:flex;flex-wrap:wrap;gap:1rem;
  align-items:center;justify-content:space-between;padding:.85rem 1.25rem;
  background:rgba(14,14,16,.9);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
header.site .brand{font-weight:700;letter-spacing:.06em;text-transform:uppercase;border:0;font-size:.95rem}
header.site .dot{display:inline-block;width:.55em;height:.55em;border-radius:50%;
  background:#fff;margin-right:.5em;vertical-align:middle;animation:pulse 2.4s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
header.site nav{display:flex;gap:1.1rem;font-size:.85rem}
header.site nav a{border:0;color:var(--mut)}
header.site nav a:hover{color:var(--fg)}
main{max-width:var(--max);margin:0 auto;padding:2rem 1.25rem 4rem}
.hero{padding:3rem 0 2rem;border-bottom:1px solid var(--line);margin-bottom:2rem}
.hero .kicker{letter-spacing:.35em;text-transform:uppercase;color:var(--mut);font-size:.72rem}
.hero h1{font-size:clamp(2.4rem,7vw,4.4rem);line-height:1.02;margin:.4rem 0 .6rem;letter-spacing:-.02em}
.hero p.tag{font-size:clamp(1.1rem,2.4vw,1.5rem);color:var(--mut);margin:0}
h2{font-size:1.5rem;margin:2.4rem 0 .8rem;letter-spacing:-.01em}
h3{font-size:1.1rem;margin:1.6rem 0 .5rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:1rem;margin:1.2rem 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;display:block;border-bottom:1px solid var(--line)}
.card:hover{border-color:#4a4a52;transform:translateY(-2px);transition:.15s}
.card .thumb{aspect-ratio:9/16;background:#0a0a0c;display:flex;align-items:center;justify-content:center;overflow:hidden}
.card .thumb img{width:100%;height:100%;object-fit:cover;display:block}
.card .thumb .mono{font-size:2rem;font-weight:700;color:#3a3a42;letter-spacing:.05em}
.card .meta{padding:.7rem .8rem .9rem}
.card .meta b{display:block;font-size:.98rem}
.card .meta span{color:var(--mut);font-size:.8rem}
.pill{display:inline-block;font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);
  border:1px solid var(--line);border-radius:999px;padding:.15em .6em;margin-left:.4em}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin:1.4rem 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:1rem}
.stat b{display:block;font-size:1.7rem;line-height:1}
.stat span{color:var(--mut);font-size:.78rem;letter-spacing:.04em}
.artist-head{display:grid;grid-template-columns:minmax(180px,260px) 1fr;gap:2rem;align-items:start;margin:1rem 0 2rem}
.artist-head img{width:100%;border-radius:12px;border:1px solid var(--line);background:#0a0a0c}
.artist-head .mono{aspect-ratio:9/16;display:flex;align-items:center;justify-content:center;font-size:3rem;
  color:#3a3a42;font-weight:700;border:1px solid var(--line);border-radius:12px;background:#0a0a0c}
article{max-width:760px}
article table{border-collapse:collapse;width:100%;font-size:.9rem;margin:1rem 0;display:block;overflow-x:auto}
article th,article td{border:1px solid var(--line);padding:.45rem .6rem;text-align:left}
article th{background:var(--panel)}
article blockquote{border-left:3px solid var(--line);margin:1rem 0;padding:.2rem 1rem;color:var(--mut)}
article code{background:#1b1b1f;padding:.1em .35em;border-radius:4px;font-size:.88em}
article pre{background:#111114;border:1px solid var(--line);border-radius:10px;padding:1rem;overflow-x:auto}
article pre code{background:none;padding:0}
article img{max-width:100%;height:auto}
.doc-list{list-style:none;padding:0;margin:1rem 0}
.doc-list li{border-bottom:1px solid var(--line);padding:.55rem 0}
.doc-list a{border:0}
.muted{color:var(--mut);font-size:.83rem}
footer.site{max-width:var(--max);margin:0 auto;padding:2rem 1.25rem 3rem;border-top:1px solid var(--line);color:var(--mut)}
@media(max-width:640px){.artist-head{grid-template-columns:1fr}}
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="7" fill="#0e0e10"/>
<circle cx="16" cy="16" r="6" fill="#f4f4f6"/>
<circle cx="16" cy="16" r="2.4" fill="#0e0e10"/></svg>
"""

# ── discovery ────────────────────────────────────────────────────────────────
def discover_artists():
    base = os.path.join(ROOT, "Season One", "Artists")
    out = []
    for name in sorted(os.listdir(base), key=lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        press = os.path.join(d, "Press")
        fine = index = notes = None
        if os.path.isdir(press):
            for f in sorted(os.listdir(press)):
                if f.startswith("FINE_PRINT_") and f.endswith(".md"):
                    fine = f"Season One/Artists/{name}/Press/{f}"
                elif f == "index.md":
                    index = f"Season One/Artists/{name}/Press/index.md"
                elif f == "RELEASE_NOTES.md":
                    notes = f"Season One/Artists/{name}/Press/RELEASE_NOTES.md"
        cover = None
        cov_dir = os.path.join(d, "EPK", "Cover")
        if os.path.isdir(cov_dir):
            files = sorted(os.listdir(cov_dir))
            for pref in ("cover_1080x1920_bw.png",):
                if pref in files:
                    cover = f"Season One/Artists/{name}/EPK/Cover/{pref}"
            if not cover:
                for f in files:
                    if f.endswith("_1080x1920.png"):
                        cover = f"Season One/Artists/{name}/EPK/Cover/{f}"
                        break
        genre = "—"
        if fine:
            for line in read(fine).splitlines():
                m = re.match(r"\s*-\s*\*\*Style\s*/\s*genres?:\*\*\s*(.+?)\s*$", line, re.I)
                if m:
                    g = m.group(1).strip()
                    genre = "New artist — TBA" if "new artist" in g.lower() else g
                    break
        out.append(dict(name=name, slug=slugify(name), cover=cover, fine=fine,
                        index=index, notes=notes, genre=genre,
                        onboarded=not (cover and index)))
    return out

def build(out):
    doc_urls = {src: f"docs/{slug}.html" for slug, _t, _p, src in DOCS if src}
    artists = discover_artists()

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "assets", "covers"), exist_ok=True)
    os.makedirs(os.path.join(out, "docs"), exist_ok=True)
    os.makedirs(os.path.join(out, "artists"), exist_ok=True)
    open(os.path.join(out, ".nojekyll"), "w").close()
    open(os.path.join(out, "assets", "style.css"), "w", encoding="utf-8").write(CSS)
    open(os.path.join(out, "assets", "favicon.svg"), "w", encoding="utf-8").write(FAVICON)

    # covers
    for a in artists:
        if a["cover"]:
            dst = os.path.join(out, "assets", "covers", a["slug"] + ".png")
            shutil.copyfile(os.path.join(ROOT, a["cover"]), dst)

    # ── index ────────────────────────────────────────────────────────────────
    cards = []
    for a in artists:
        thumb = (f'<img loading="lazy" src="assets/covers/{a["slug"]}.png" alt="{esc(a["name"])} cover">'
                 if a["cover"] else
                 f'<span class="mono">{esc("".join(w[0] for w in a["name"].split()[:2]).upper())}</span>')
        pill = '<span class="pill">Onboarded</span>' if a["onboarded"] else ""
        cards.append(
            f'<a class="card" href="artists/{a["slug"]}.html">'
            f'<span class="thumb">{thumb}</span>'
            f'<span class="meta"><b>{esc(a["name"])}{pill}</b>'
            f'<span>{esc(a["genre"])}</span></span></a>')
    body = f"""<section class="hero">
  <p class="kicker">{SEASON} · {len(artists)} artists · 2026</p>
  <h1>{SITE_NAME}</h1>
  <p class="tag">{TAGLINE} — a DJ &amp; performing-artist lab. Live sessions, mastered to one house standard.</p>
</section>
<section id="about">
  <p>The Radio-ish Lab records live DJ and performing-artist sessions and masters them to a single
  house standard: one EQ across every deck, <strong>−14 LUFS</strong> integrated, true peak below
  <strong>0 dBTP</strong>, and a mandatory QC gate that fails the build. {SEASON} collects
  {len(artists)} acts — from six-hour continuous techno sessions to a 2004 archival transfer —
  into one coherent catalogue.</p>
</section>
<section id="roster">
  <h2>Roster</h2>
  <div class="grid">{''.join(cards)}</div>
</section>
<section id="evidence">
  <h2>Evidence</h2>
  <div class="stats">
    <div class="stat"><b>15/15</b><span>masters on the house standard</span></div>
    <div class="stat"><b>123/123</b><span>mix QC checks passed</span></div>
    <div class="stat"><b>150/150</b><span>EPK QC checks passed</span></div>
    <div class="stat"><b>516</b><span>source drop-outs bridged</span></div>
  </div>
  <p class="muted">Every master, loop, video and cover is measured, not asserted. Full figures and the
  build pipeline live in the <a href="evidence.html">evidence</a> and <a href="docs/index.html">docs</a>.</p>
</section>
<section id="credits">
  <h2>Credits</h2>
  <p>Radio-ish Lab is <strong>created by William Majanja and DJ Bernie Cyber</strong>. Production is
  <strong>funded by B4 Hotel Management</strong>.</p>
  <p class="muted">Produced by Agent Mgumbe Studio · Developed by Schrödinger’s Breakfast
  (1nf1D3L [William Majanja]) for Before Hotel Management (B4) · Executive Producer Bernie.</p>
</section>"""
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page("Season One", body))

    # ── artist pages ─────────────────────────────────────────────────────────
    for a in artists:
        if a["cover"]:
            media = f'<img src="../assets/covers/{a["slug"]}.png" alt="{esc(a["name"])} cover">'
        else:
            media = f'<div class="mono">{esc("".join(w[0] for w in a["name"].split()[:2]).upper())}</div>'
        parts = [f'<p class="muted"><a href="../index.html">← All artists</a></p>',
                 f'<div class="artist-head">{media}<div>'
                 f'<p class="kicker">{SEASON}</p><h1 style="margin:.2rem 0">{esc(a["name"])}</h1>'
                 f'<p class="tag" style="color:var(--mut)">{esc(a["genre"])}'
                 + ('<span class="pill">Onboarded</span>' if a["onboarded"] else "") + "</p></div></div>"]
        if a["fine"]:
            parts.append('<article>' + rewrite_links(render_md(read(a["fine"])), a["fine"], doc_urls, f'artists/{a["slug"]}.html') + "</article>")
        if a["index"]:
            parts.append("<h2>Press one-pager</h2><article>" +
                         rewrite_links(render_md(read(a["index"])), a["index"], doc_urls, f'artists/{a["slug"]}.html') + "</article>")
        if a["notes"]:
            parts.append("<h2>Release notes</h2><article>" +
                         rewrite_links(render_md(read(a["notes"])), a["notes"], doc_urls, f'artists/{a["slug"]}.html') + "</article>")
        parts.append(f'<p class="muted">Media masters are not in git — see the project on '
                     f'<a href="{REPO_URL}">GitHub</a> for the pipeline and QC evidence.</p>')
        open(os.path.join(out, "artists", a["slug"] + ".html"), "w", encoding="utf-8").write(
            page(a["name"], "\n".join(parts), depth=1, description=f"{a['name']} — {a['genre']} · {SITE_NAME} {SEASON}"))

    # ── docs ─────────────────────────────────────────────────────────────────
    doc_rows = "".join(
        f'<li><a href="{slug}.html">{esc(nav)}</a> <span class="muted">— {esc(ptitle)}</span></li>'
        for slug, nav, ptitle, _src in NAV_DOCS)
    open(os.path.join(out, "docs", "index.html"), "w", encoding="utf-8").write(page(
        "Docs", f"<h1>Docs</h1><p>The project's written record — the same files as in the repo.</p>"
                f"<ul class=\"doc-list\">{doc_rows}</ul>", depth=1))

    for slug, _nav, ptitle, src in NAV_DOCS:
        raw = read(src)
        if src.endswith(".md"):
            body_html = render_md(raw)
            if src.endswith("INDEX.md") and src.startswith("EPK_Project"):
                pass
            body_html = rewrite_links(body_html, src, doc_urls, f"docs/{slug}.html")
        else:  # LICENSE
            body_html = "<pre>" + esc(raw) + "</pre>"
        body = (f'<p class="muted"><a href="index.html">← Docs</a></p>'
                f'<article>{body_html}</article>')
        open(os.path.join(out, "docs", slug + ".html"), "w", encoding="utf-8").write(
            page(ptitle, body, depth=1))

    # ── evidence ─────────────────────────────────────────────────────────────
    ev = f"""<h1>Evidence</h1>
<p>{SEASON} is proved rather than asserted. Every deliverable is measured and the figures are published.</p>
<div class="stats">
  <div class="stat"><b>15</b><span>full-length masters</span></div>
  <div class="stat"><b>123/123</b><span>mix QC checks</span></div>
  <div class="stat"><b>150/150</b><span>EPK QC checks</span></div>
  <div class="stat"><b>516</b><span>drop-outs bridged</span></div>
</div>
<h2>Reports</h2>
<ul class="doc-list">
  <li><a href="docs/mix-qc.html">Mix QC report</a> <span class="muted">— house standard, per-artist measured trim / loudness / true peak, ceiling repairs, drop-out gate</span></li>
  <li><a href="docs/epk-qc.html">EPK QC report</a> <span class="muted">— loop, video, cover and fine-print checks</span></li>
  <li><a href="docs/evidence.html">Release checklist</a> <span class="muted">— the full verified-item list</span></li>
  <li><a href="docs/research-paper.html">Season One research paper</a> <span class="muted">— method, results and the operator-side fault analysis</span></li>
</ul>
<h2>Manifests</h2>
<p class="muted">Byte-level SHA-256 manifests cover the EPK deliverables and the full media tree.
The media masters themselves are not in git; the manifests and the build pipeline are.</p>
<p class="muted"><a href="{REPO_URL}/tree/{BRANCH}/qc">qc/ on GitHub →</a></p>"""
    open(os.path.join(out, "evidence.html"), "w", encoding="utf-8").write(page("Evidence", ev))

    print(f"  built {out}/ — {len(artists)} artists, {len(NAV_DOCS)} docs")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="_site")
    build(ap.parse_args().out)
