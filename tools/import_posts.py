#!/usr/bin/env python3
"""Import WordPress posts and pages into Hugo page bundles.

Source: REST API snapshots in _import/api/ (posts.json, pages.json,
categories.json, tags.json), attachment metadata from
_import/wordpress-export.xml and original images from _import/uploads/.

Usage (from repo root):
    python3 -I tools/import_posts.py [bundle ...]

Without arguments all bundles listed in PAIRS and all PAGES are imported.
Existing index.de.md / index.en.md files of the selected bundles are
overwritten; pages only get index.de.md, index.en.md stays untouched.
A JSON log of findings is written to _import/import-log.json.
"""

import html
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent
IMPORT = ROOT / "_import"
API = IMPORT / "api"
UPLOADS = IMPORT / "uploads"
POSTS_DIR = ROOT / "content" / "posts"

SITE_HOST = "dbavonnebenan.de"
SITE_TZ = ZoneInfo("Europe/Berlin")
LANG_TAGS = {"de", "eng"}

# bundle folder -> (old DE slug, old EN slug)
PAIRS = {
    "reporting-sql-server-blocks": ("reporting-sql-server-blocks-de", "reporting-sql-server-blocks-en"),
    "sql-server-sysadmin-role-can-override-the-default-schema": (
        "sql-server-sysadmin-role-can-override-the-default-schema-de",
        "sql-server-sysadmin-role-can-override-the-default-schema-en",
    ),
    "sql-server-truncate-vs-delete-dml-or-ddl": (
        "sql-server-truncate-vs-delete-dml-or-ddl-de",
        "sql-server-truncate-vs-delete-dml-or-ddl-en",
    ),
    "powershell-classes-for-beginner": ("powershell-classes-for-beginner-de", "powershell-classes-for-beginner-en"),
    "sql-server-disk-latency": ("sql-server-disk-latency-de", "sql-server-disk-latency-en"),
    "psterminalperfcounter-speedup-your-performance-counters": (
        "psterminalperfcounter-speedup-your-performance-counters_de",
        "psterminalperfcounter-speedup-your-performance-counters_en",
    ),
    "automate-sql-server-ha-ad-spn-and-cluster-setup": (
        "automate-sql-server-ha-ad-spn-and-cluster-setup_de",
        "automate-sql-server-ha-ad-spn-and-cluster-setup_en",
    ),
    "windows-performance-counters-how-the-os-monitors-itself": (
        "windows-performance-counters-how-the-os-monitors-itself_de",
        "windows-performance-counters-how-the-os-monitors-itself_en",
    ),
    "psterminalperfcounter-counter-in-terminal-handson": (
        "psterminalperfcounter-counter-in-terminal-handson_de",
        "psterminalperfcounter-counter-in-terminal-handson_en",
    ),
}

# WordPress pages, German only; English versions are maintained by hand
PAGES = ("about", "impressum", "privacy-policy")
PAGES_DIR = ROOT / "content"

# old slug -> (bundle, lang)
SLUG_MAP = {}
for _bundle, (_de, _en) in PAIRS.items():
    SLUG_MAP[_de] = (_bundle, "de")
    SLUG_MAP[_en] = (_bundle, "en")

BRUSH_LANG = {"powershell": "powershell", "sql": "sql", "plain": None}
SIZE_SUFFIX = re.compile(r"-(\d+x\d+|scaled)(?=\.\w+$)")
UPLOAD_URL = re.compile(r"^https?://(?:www\.)?" + re.escape(SITE_HOST) + r"/wp-content/uploads/(\d{4}/\d{2}/[^?#]+)")
SITE_URL = re.compile(r"^https?://(?:www\.)?" + re.escape(SITE_HOST) + r"(/[^#?]*)?([?#].*)?$")


def load_json(name):
    return json.loads((API / name).read_text(encoding="utf-8"))


def load_attachments():
    """Return {attachment id: (upload path, alt text)} from the WXR export."""
    ns = {"wp": "http://wordpress.org/export/1.2/"}
    result = {}
    root = ET.parse(IMPORT / "wordpress-export.xml").getroot()
    for item in root.find("channel").findall("item"):
        if item.findtext("wp:post_type", namespaces=ns) != "attachment":
            continue
        url = item.findtext("wp:attachment_url", namespaces=ns)
        alt = ""
        for meta in item.findall("wp:postmeta", namespaces=ns):
            if meta.findtext("wp:meta_key", namespaces=ns) == "_wp_attachment_image_alt":
                alt = meta.findtext("wp:meta_value", namespaces=ns) or ""
        result[int(item.findtext("wp:post_id", namespaces=ns))] = (url.split("/wp-content/uploads/")[1], alt)
    return result


def yaml_str(value):
    # JSON strings are valid YAML double-quoted scalars
    return json.dumps(value, ensure_ascii=False)


def wp_date(value):
    return datetime.fromisoformat(value).replace(tzinfo=SITE_TZ).isoformat()


def plain_text(fragment):
    text = BeautifulSoup(fragment, "html.parser").get_text(" ")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return re.sub(r"\s*\[(?:…|&hellip;|\.\.\.)\]\s*$", "", text)


class Converter:
    """Convert rendered WordPress HTML of one post into Markdown."""

    def __init__(self, bundle_dir, lang, log):
        self.bundle_dir = bundle_dir
        self.lang = lang
        self.log = log
        self.images = set()

    # ---------- images and links ----------

    def image(self, img, title=None):
        src = img.get("src", "")
        alt = (img.get("alt") or "").strip()
        m = UPLOAD_URL.match(src)
        if not m:
            self.log.append(f"externes Bild nicht übernommen: {src}")
            return ""
        rel = SIZE_SUFFIX.sub("", html.unescape(m.group(1)))
        source = UPLOADS / rel
        if not source.exists():
            self.log.append(f"Bild fehlt in uploads: {rel}")
            return ""
        name = source.name
        target = self.bundle_dir / name
        if target.exists() and name not in self.images and target.read_bytes() != source.read_bytes():
            self.log.append(f"Namenskonflikt Bild: {rel}")
        shutil.copy2(source, target)
        self.images.add(name)
        suffix = f' "{title}"' if title else ""
        return f"![{self.escape_link_text(alt)}]({name}{suffix})"

    def link_target(self, href):
        href = html.unescape(href or "").strip()
        broken = re.match(r"^https?://\\/(.*)$", href)
        if broken:
            self.log.append(f"defekter Link repariert: {href}")
            href = "/" + broken.group(1)
        if href.startswith("/") and not href.startswith("//"):
            href = f"https://{SITE_HOST}{href}"
        m = SITE_URL.match(href)
        if not m:
            return href
        path = (m.group(1) or "/").strip("/")
        suffix = m.group(2) or ""
        if path in SLUG_MAP:
            bundle, lang = SLUG_MAP[path]
            if lang != self.lang:
                self.log.append(f"interner Link in andere Sprache: {href}")
            return f"../{bundle}/index.{lang}.md{suffix}"
        if path in ("about", "impressum", "privacy-policy"):
            return f"/{path}/{suffix}"
        if UPLOAD_URL.match(href):
            self.log.append(f"Link auf Upload-Datei: {href}")
        else:
            self.log.append(f"interner Link ohne Ziel: {href}")
        return href

    @staticmethod
    def escape_link_text(text):
        return text.replace("[", r"\[").replace("]", r"\]")

    # ---------- inline ----------

    @staticmethod
    def escape_text(text):
        text = text.replace("\\", "\\\\")
        text = re.sub(r"([*`\[\]<])", r"\\\1", text)
        # underscores only at word boundaries, intraword ones are literal in CommonMark
        text = re.sub(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])", r"\\_", text)
        return text

    def inline(self, node):
        parts = []
        for child in node.children:
            if isinstance(child, NavigableString):
                if child.__class__.__name__ == "Comment":
                    continue
                parts.append(self.escape_text(re.sub(r"\s+", " ", str(child))))
                continue
            if not isinstance(child, Tag):
                continue
            name = child.name
            if name == "br":
                parts.append("  \n")
            elif name in ("strong", "b"):
                parts.append(self.wrap(self.inline(child), "**"))
            elif name in ("em", "i"):
                parts.append(self.wrap(self.inline(child), "*"))
            elif name == "del":
                parts.append(self.wrap(self.inline(child), "~~"))
            elif name == "code":
                link = child.find("a")
                if link is not None and link.get("href"):
                    # <code><a>x</a></code> -> linked code span
                    parts.append(f"[{self.code_span(child.get_text())}]({self.link_target(link['href'])})")
                else:
                    parts.append(self.code_span(child.get_text()))
            elif name == "a":
                parts.append(self.anchor(child))
            elif name == "img":
                parts.append(self.image(child))
            else:
                parts.append(self.inline(child))
        return "".join(parts)

    @staticmethod
    def wrap(text, marker):
        # keep surrounding whitespace and hard breaks outside the delimiters
        m = re.match(r"^(\s*)(.*?)(\s*)$", text, re.S)
        lead, inner, trail = m.groups()
        if not inner:
            return text
        return f"{lead}{marker}{inner}{marker}{trail}"

    @staticmethod
    def code_span(text):
        text = re.sub(r"\s+", " ", text)
        ticks = "``" if "`" in text else "`"
        pad = " " if text.startswith("`") or text.endswith("`") else ""
        return f"{ticks}{pad}{text}{pad}{ticks}"

    def anchor(self, a):
        if a.find("img"):
            images = "".join(self.image(img) for img in a.find_all("img"))
            href = a.get("href", "")
            if UPLOAD_URL.match(href) or SITE_URL.match(href):
                return images
            return f"[{images}]({self.link_target(href)})"
        if a.find("code"):
            # mixed code/text link text -> one code span
            text = self.code_span(a.get_text()) if a.get_text().strip() else ""
        else:
            text = self.inline(a).strip()
        href = a.get("href")
        if not href:
            return text
        if not text:
            return ""
        return f"[{text}]({self.link_target(href)})"

    # ---------- blocks ----------

    def blocks(self, node):
        out = []
        for child in node.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text and child.__class__.__name__ != "Comment":
                    out.append(self.escape_text(text))
                continue
            if isinstance(child, Tag):
                out.extend(self.block(child))
        return [b for b in out if b and b.strip()]

    def block(self, el):
        name = el.name
        classes = el.get("class", [])

        if "wp-block-spacer" in classes:
            return []
        if "vlp-link-container" in classes:
            return [self.link_preview(el)]
        if "wp-block-syntaxhighlighter-code" in classes or name == "pre":
            pre = el if name == "pre" else el.find("pre")
            return [self.code_block(pre)] if pre else []
        if "ub-styled-box" in classes:
            # "what to expect" box, replaced by the table of contents
            return []
        if "wp-block-columns" in classes:
            return self.columns(el)
        if "wp-block-group" in classes and "is-nowrap" in classes:
            # side by side group: images row, or text followed by emote
            if self.only_images(el):
                images = [self.image(img, "emote") for img in el.find_all("img")]
                return [" ".join(i for i in images if i)]
            return self.side_by_side(el.find_all(recursive=False))
        if name == "p":
            text = self.merge_links(self.inline(el).strip())
            # icon line break: "⚒️<br>code" -> "⚒️ code"
            text = re.sub(r"^([^\w\s\\\[`*]{1,3})  \n", r"\1 ", text)
            return [self.guard_block_start(text)] if text else []
        if re.fullmatch(r"h[1-6]", name):
            text = self.inline(el).strip()
            if not text:
                return []
            # drop bold that wraps the whole heading, headings are bold anyway
            text = re.sub(r"^\*\*(.+)\*\*$", r"\1", text)
            anchor = f" {{#{el['id']}}}" if el.get("id") else ""
            return [f"{'#' * int(name[1])} {text}{anchor}"]
        if name in ("ul", "ol"):
            return [self.list_block(el)]
        if name == "figure":
            return self.figure(el)
        if name == "hr":
            return ["---"]
        if name == "blockquote":
            return [self.quote(self.blocks(el))]
        if name == "details":
            return self.details(el)
        if name == "img":
            return [self.image(el)]
        if name == "table":
            self.log.append("Tabelle gefunden, manuell prüfen")
        return self.blocks(el)

    def github_card(self, parts):
        """GitHub logo next to a single GitHub link -> link card."""
        logo = [p for p in parts if self.only_images(p) and p.find("img", src=re.compile(r"GitHub_"))]
        rest = [p for p in parts if p not in logo]
        links = [a for p in rest for a in p.find_all("a", href=re.compile(r"^https://github\.com/"))]
        if len(logo) != 1 or len(links) != 1:
            return None
        href = links[0]["href"]
        text = self.escape_text(links[0].get_text(" ", strip=True)) or href
        return f'[{text}]({href} "{href.split("://", 1)[1]}")'

    @staticmethod
    def only_images(el):
        """True if the element holds images but no text."""
        return bool(el.find("img")) and not el.get_text(strip=True)

    def columns(self, el):
        return self.side_by_side(el.find_all(class_="wp-block-column", recursive=False))

    def side_by_side(self, parts):
        card = self.github_card(parts)
        if card:
            return [card]
        # image-only parts become small centered emotes after the text
        images, text = [], []
        for part in parts:
            if self.only_images(part):
                images.extend(self.image(img, "emote") for img in part.find_all("img"))
            else:
                text.extend(self.block(part))
        images = [i for i in images if i]
        return text + ([" ".join(images)] if images else [])

    @staticmethod
    def merge_links(text):
        """Join adjacent links with the same target, e.g. [`a`](u)[`.`md](u)."""
        pattern = re.compile(r"\[`([^`\]]+)`\]\(([^)\s]+)\)\[`([^`\]]+)`\]\(\2\)")
        while True:
            merged = pattern.sub(lambda m: f"[`{m.group(1)}{m.group(3)}`]({m.group(2)})", text)
            if merged == text:
                return text
            text = merged

    @staticmethod
    def guard_block_start(text):
        # prevent paragraphs from turning into headings, lists or rules
        if re.match(r"^(#{1,6}\s|[-+>]\s|\d+[.)]\s|={3,}|-{3,})", text):
            return "\\" + text
        return text

    def link_preview(self, el):
        a = el.find("a", class_="vlp-link")
        title_el = el.find(class_="vlp-link-title")
        href = a.get("href", "") if a else ""
        title = title_el.get_text(" ", strip=True) if title_el else (a.get("title", "") if a else href)
        title = html.unescape(title) or href
        summary_el = el.find(class_="vlp-link-summary")
        summary = html.unescape(summary_el.get_text(" ", strip=True)) if summary_el else ""
        summary = summary.replace('"', "'") or title
        # a link with title renders as card (see custom.css)
        return f'[{self.escape_text(title)}]({self.link_target(href)} "{summary}")'

    def code_block(self, pre):
        match = re.search(r"brush:\s*([\w-]+)", " ".join(pre.get("class", [])))
        brush = match.group(1) if match else None
        lang = BRUSH_LANG.get(brush, brush)
        code = pre.get_text()
        code = code.replace("\r\n", "\n").strip("\n")
        code = "\n".join(line.rstrip() for line in code.split("\n"))
        if not lang:
            lang = self.guess_language(code)
            self.log.append(f"Code-Sprache geraten ({brush} -> {lang}): {code.splitlines()[0][:60] if code else ''}")
        fence = "```"
        while fence in code:
            fence += "`"
        return f"{fence}{lang}\n{code}\n{fence}"

    @staticmethod
    def guess_language(code):
        if code.lstrip().startswith(("{", "[")) and re.search(r'"\w+"\s*:', code):
            return "json"
        if re.search(r"\b(select|insert|update|delete|create|alter|exec)\b.*\b(from|table|procedure|into)\b", code, re.I | re.S):
            return "sql"
        if re.search(r"\$\w+|\b(Get|Set|New|Invoke|Import|Install|Test|Start)-\w+", code):
            return "powershell"
        return "text"

    def list_block(self, el, depth=0):
        lines = []
        ordered = el.name == "ol"
        for i, li in enumerate(el.find_all("li", recursive=False), start=1):
            marker = f"{i}." if ordered else "-"
            indent = "  " * depth if not ordered else "   " * depth
            nested = []
            inline_parts = []
            for child in li.children:
                if isinstance(child, Tag) and child.name in ("ul", "ol"):
                    nested.append(self.list_block(child, depth + 1))
                elif isinstance(child, Tag) and child.name in ("p", "div", "figure"):
                    inline_parts.append(" ".join(self.block(child)))
                else:
                    wrapper = BeautifulSoup("<span></span>", "html.parser").span
                    wrapper.append(child.__copy__() if isinstance(child, Tag) else NavigableString(str(child)))
                    inline_parts.append(self.inline(wrapper))
            text = re.sub(r"[ \t]+", " ", "".join(inline_parts)).strip()
            text = text.replace("  \n", "  \n" + indent + "  ")
            lines.append(f"{indent}{marker} {text}")
            lines.extend(nested)
        return "\n".join(lines)

    def figure(self, el):
        out = []
        img = el.find("img")
        if img is not None:
            a = img.find_parent("a")
            if a is not None and a.find_parent("figure") is el:
                out.append(self.anchor(a))
            else:
                out.append(self.image(img, "emote" if self.is_small(img) else None))
        caption = el.find("figcaption")
        if caption is not None:
            text = self.inline(caption).strip()
            if text:
                out.append(f"*{text}*")
        return out

    @staticmethod
    def is_small(img):
        """Images scaled down to a small fixed width in WordPress (emotes)."""
        match = re.search(r"width:\s*(\d+)px", img.get("style", ""))
        return bool(match) and int(match.group(1)) <= 200

    @staticmethod
    def quote(blocks):
        body = "\n\n".join(blocks)
        return "\n".join(("> " + line) if line else ">" for line in body.split("\n"))

    def details(self, el):
        summary = el.find("summary")
        title = summary.get_text(" ", strip=True) if summary else ""
        if summary is not None:
            summary.extract()
        inner = self.blocks(el)
        title = html.unescape(title).replace('"', "'")
        return [f'{{{{< details summary="{title}" >}}}}', *inner, "{{< /details >}}"]

    def convert(self, rendered):
        soup = BeautifulSoup(rendered, "html.parser")
        md = "\n\n".join(self.blocks(soup))
        md = re.sub(r"\n{3,}", "\n\n", md)
        return md.strip() + "\n"


def front_matter(post, bundle, lang, cats, tags, attachments, aliases):
    lines = ["---"]
    lines.append(f"title: {yaml_str(html.unescape(post['title']['rendered']))}")
    lines.append(f"slug: {yaml_str(bundle)}")
    lines.append(f"date: {wp_date(post['date'])}")
    lines.append(f"lastmod: {wp_date(post['modified'])}")
    lines.append("draft: false")
    lines.append("categories: [" + ", ".join(yaml_str(cats[c]) for c in post["categories"]) + "]")
    post_tags = [tags[t] for t in post["tags"] if tags[t].lower() not in LANG_TAGS]
    lines.append("tags: [" + ", ".join(yaml_str(t) for t in post_tags) + "]")
    lines.append(f"summary: {yaml_str(plain_text(post['excerpt']['rendered']))}")
    if aliases:
        lines.append("aliases:")
        lines.extend(f"  - {a}" for a in aliases)
    featured = attachments.get(post.get("featured_media") or 0)
    if featured:
        rel, alt = featured
        lines.append("cover:")
        lines.append(f"  image: {yaml_str(Path(rel).name)}")
        lines.append(f"  alt: {yaml_str(alt)}")
        lines.append("  relative: true")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def import_bundle(bundle, posts, cats, tags, attachments, report):
    bundle_dir = POSTS_DIR / bundle
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for lang, old_slug in zip(("de", "en"), PAIRS[bundle]):
        post = posts[old_slug]
        log = []
        conv = Converter(bundle_dir, lang, log)
        body = conv.convert(post["content"]["rendered"])
        featured = attachments.get(post.get("featured_media") or 0)
        if featured:
            source = UPLOADS / featured[0]
            shutil.copy2(source, bundle_dir / source.name)
            conv.images.add(source.name)
        # old URLs had no language prefix; "../" lifts EN aliases out of /en/
        prefix = "" if lang == "de" else ".."
        aliases = [f"{prefix}/{old_slug}/"] if old_slug != bundle else []
        text = front_matter(post, bundle, lang, cats, tags, attachments, aliases) + body
        (bundle_dir / f"index.{lang}.md").write_text(text, encoding="utf-8")
        report[f"{bundle}/{lang}"] = {"old_slug": old_slug, "images": sorted(conv.images), "log": log}


def import_page(page, report):
    page_dir = PAGES_DIR / page["slug"]
    page_dir.mkdir(parents=True, exist_ok=True)
    log = []
    conv = Converter(page_dir, "de", log)
    body = conv.convert(page["content"]["rendered"])
    lines = [
        "---",
        f"title: {yaml_str(html.unescape(page['title']['rendered']))}",
        f"date: {wp_date(page['date'])}",
        f"lastmod: {wp_date(page['modified'])}",
        "draft: false",
        "hideMeta: true",
        "ShowToc: false",
        "ShowReadingTime: false",
        "ShowPostNavLinks: false",
        "---",
    ]
    (page_dir / "index.de.md").write_text("\n".join(lines) + "\n\n" + body, encoding="utf-8")
    report[f"{page['slug']}/de"] = {"old_slug": page["slug"], "images": sorted(conv.images), "log": log}


def main(argv):
    selected = argv or list(PAIRS) + list(PAGES)
    unknown = [b for b in selected if b not in PAIRS and b not in PAGES]
    if unknown:
        sys.exit(f"unknown bundle(s): {', '.join(unknown)}")
    posts = {p["slug"]: p for p in load_json("posts.json")}
    cats = {c["id"]: html.unescape(c["name"]) for c in load_json("categories.json")}
    tags = {t["id"]: html.unescape(t["name"]) for t in load_json("tags.json")}
    attachments = load_attachments()
    report = {}
    pages = {p["slug"]: p for p in load_json("pages.json")}
    for bundle in selected:
        if bundle in PAGES:
            import_page(pages[bundle], report)
        else:
            import_bundle(bundle, posts, cats, tags, attachments, report)
    log_file = IMPORT / "import-log.json"
    existing = json.loads(log_file.read_text(encoding="utf-8")) if log_file.exists() else {}
    existing.update(report)
    log_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    for key, entry in report.items():
        print(f"{key}: {len(entry['images'])} Bilder, {len(entry['log'])} Hinweise")
        for line in entry["log"]:
            print(f"    {line}")


if __name__ == "__main__":
    main(sys.argv[1:])
