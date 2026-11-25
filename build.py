#!/usr/bin/env python3
"""Tiny static-site builder for notary.augello.net (standard library only).

    python3 build.py            build into ./dist and report problems
    python3 build.py --strict   same, but exit 1 if anything is unfinished
    python3 build.py --github   GitHub Pages build (adds .nojekyll and CNAME)

Pages live in src/pages/**.html: `key: value` header lines, a line with ---,
then the body. Shared head/header/footer live in src/partials/.
"""
import datetime, html, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC, DIST = ROOT / "src", ROOT / "dist"
HOST = "notary.augello.net"
SITE = "https://" + HOST
STRICT = "--strict" in sys.argv
GITHUB = "--github" in sys.argv
problems = []


def fill(t, v):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(v.get(m.group(1), m.group(0))), t)


def parse(p):
    head, sep, body = p.read_text(encoding="utf-8").partition("\n---\n")
    if not sep:
        sys.exit(f"{p}: missing '---' separator")
    meta = {}
    for line in head.splitlines():
        if line.strip():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    for k in ("title", "description", "path"):
        if k not in meta:
            sys.exit(f"{p}: missing '{k}:' header")
    return meta, body


def out_file(u):
    if u.endswith(".html"):
        return DIST / u.lstrip("/")
    return DIST / "index.html" if u == "/" else DIST / u.strip("/") / "index.html"


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(SRC / "assets", DIST / "assets")
    P = {n: (SRC / "partials" / f"{n}.html").read_text(encoding="utf-8") for n in ("head", "header", "footer")}
    year, pages = datetime.date.today().year, []
    for f in sorted((SRC / "pages").rglob("*.html")):
        meta, body = parse(f)
        nav = meta.get("nav", "")
        v = {
            "title": html.escape(meta["title"], quote=True),
            "description": html.escape(meta["description"], quote=True),
            "canonical": SITE + meta["path"],
            "robots": meta.get("robots", "index, follow, max-image-preview:large"),
            "c_faq": ' aria-current="page"' if nav == "faq" else "",
            "year": year,
        }
        head = fill(P["head"], v)
        if meta["path"].endswith(".html"):
            head = head.replace(f'<link rel="canonical" href="{v["canonical"]}">\n', "")
        page = ('<!doctype html>\n<html lang="en">\n<head>\n' + head + "</head>\n<body>\n"
                '<a class="skip" href="#main">Skip to content</a>\n' + fill(P["header"], v)
                + '<main id="main">\n' + body.strip() + "\n</main>\n" + fill(P["footer"], v) + "</body>\n</html>\n")
        t = out_file(meta["path"])
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(page, encoding="utf-8")
        pages.append((meta, t, page))
        if len(re.findall(r"<h1[ >]", page)) != 1:
            problems.append(f"{meta['path']}: needs exactly one <h1>")
        n = page.count('class="todo"')
        if n:
            problems.append(f"{meta['path']}: {n} yellow placeholder(s) still to fill in")
    urls = [m["path"] for m, _, _ in pages if "noindex" not in m.get("robots", "")]
    today = datetime.date.today().isoformat()
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
        + "</urlset>\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    if GITHUB:
        (DIST / ".nojekyll").write_text("", encoding="utf-8")
        (DIST / "CNAME").write_text(HOST + "\n", encoding="utf-8")
    ids = {t: set(re.findall(r'\sid="([^"]+)"', pg)) for _, t, pg in pages}
    for meta, t, pg in pages:
        for ref in sorted(set(re.findall(r'(?:href|src)="([^"]+)"', pg))):
            if re.match(r"(https?:|mailto:|tel:|sms:|data:)", ref):
                continue
            path, _, frag = ref.partition("#")
            if path and not path.startswith("/"):
                problems.append(f"{meta['path']}: relative link '{ref}'")
                continue
            tgt = t if not path else (DIST / path.lstrip("/") if Path(path).suffix else out_file(path))
            if not tgt.exists():
                problems.append(f"{meta['path']}: missing file for '{ref}'")
            elif frag and tgt.suffix == ".html" and frag not in ids.get(tgt, set()):
                problems.append(f"{meta['path']}: no #{frag} anchor on {path or 'this page'}")
    print(f"Built {len(pages)} pages into dist/")
    print(f"{len(problems)} thing(s) to finish:" if problems else "No problems found.")
    for p in problems:
        print("  -", p)
    if STRICT and problems:
        sys.exit(1)


main()
