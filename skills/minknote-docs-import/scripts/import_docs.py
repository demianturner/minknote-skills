#!/usr/bin/env python3
"""Export MinkNote markdown notes into a Jekyll documentation section."""

from __future__ import annotations

import argparse
import fnmatch
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

CATEGORY_DIRS = {
    "howto": ("howto", "HowTo"),
    "reference": ("reference", "Reference"),
}
YOUTUBE_RE = re.compile(r"\{\{youtube:([A-Za-z0-9_-]+)\}\}")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\((i/[^)]+)\)")
NOTE_LINK_RE = re.compile(r"\[([^\]]+)\]\(minknote://open/([0-9A-Fa-f-]+)\)")
FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)\Z", re.S)
LEADING_NUM_RE = re.compile(r"^\d+\.\s*")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.M)


@dataclass(frozen=True)
class ImportConfig:
    source: Path
    site_root: Path
    docs_path: Path
    nav_data_path: Path
    base_url: str
    layout: str
    ignore: tuple[str, ...]

    @property
    def docs_root(self) -> Path:
        return self.site_root / self.docs_path

    @property
    def nav_data_file(self) -> Path:
        return self.site_root / self.nav_data_path


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, match.group(2).lstrip("\n")


def slugify(title: str) -> str:
    slug = LEADING_NUM_RE.sub("", title).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "page"


def display_title(title: str) -> str:
    return LEADING_NUM_RE.sub("", title).strip()


def category_for(relative: Path) -> tuple[str, str]:
    parts = [part.lower() for part in relative.parts]
    if "howto" in parts:
        return CATEGORY_DIRS["howto"]
    if "reference" in parts:
        return CATEGORY_DIRS["reference"]
    return "getting-started", "Getting Started"


def sort_key(title: str) -> tuple[int, str]:
    match = re.match(r"^(\d+)\.\s+", title)
    number = int(match.group(1)) if match else 100
    return number, display_title(title).lower()


def yaml_escape(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def youtube_embed(video_id: str) -> str:
    return (
        '<div class="docs-embed">\n'
        f'  <iframe src="https://www.youtube-nocookie.com/embed/{video_id}" '
        'title="YouTube video" allow="accelerometer; autoplay; clipboard-write; '
        "encrypted-media; gyroscope; picture-in-picture; web-share\" "
        "allowfullscreen loading=\"lazy\"></iframe>\n"
        "</div>"
    )


def strip_matching_h1(body: str, titles: set[str]) -> str:
    match = H1_RE.search(body)
    if not match:
        return body
    heading = LEADING_NUM_RE.sub("", match.group(1)).strip()
    wanted = {LEADING_NUM_RE.sub("", title).strip() for title in titles}
    if heading not in wanted:
        return body
    return (body[: match.start()] + body[match.end() :]).lstrip("\n")


def clean_url_part(value: str) -> str:
    return value.strip("/")


def permalink_for(base_url: str, category: str, slug: str, is_index: bool) -> str:
    base = "/" + clean_url_part(base_url)
    if is_index:
        return f"{base}/"
    if category == "getting-started":
        return f"{base}/{slug}/"
    return f"{base}/{category}/{slug}/"


def output_path(docs_root: Path, category: str, slug: str, is_index: bool) -> Path:
    if is_index:
        return docs_root / "index.md"
    if category == "getting-started":
        return docs_root / f"{slug}.md"
    return docs_root / category / f"{slug}.md"


def should_ignore(relative: Path, ignore: tuple[str, ...]) -> bool:
    relative_path = relative.as_posix()
    filename = relative.name
    return any(
        fnmatch.fnmatchcase(relative_path, pattern) or fnmatch.fnmatchcase(filename, pattern)
        for pattern in ignore
    )


def collect_notes(config: ImportConfig) -> list[dict]:
    notes = []
    for path in sorted(config.source.rglob("*.md")):
        relative = path.relative_to(config.source)
        if should_ignore(relative, config.ignore):
            continue
        text = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        title = meta.get("title") or path.stem
        category, category_label = category_for(relative)
        notes.append(
            {
                "path": path,
                "uuid": meta.get("uuid", "").upper(),
                "title": display_title(title),
                "source_title": title,
                "category": category,
                "category_label": category_label,
                "body": body,
                "order": sort_key(title),
            }
        )

    notes.sort(key=lambda note: (note["category"], note["order"]))

    used_slugs: dict[str, int] = {}
    index_assigned = False
    for note in notes:
        slug = slugify(note["title"])
        is_index = (not index_assigned) and note["category"] == "getting-started"
        if is_index:
            index_assigned = True
            slug = "index"
        else:
            count = used_slugs.get(slug, 0) + 1
            used_slugs[slug] = count
            if count > 1:
                slug = f"{slug}-{count}"
        note["slug"] = slug
        note["is_index"] = is_index
        note["permalink"] = permalink_for(config.base_url, note["category"], slug, is_index)
    return notes


def image_url(config: ImportConfig, category: str, filename: str) -> str:
    base = "/" + clean_url_part(config.base_url)
    return f"{base}/images/{quote(f'{category}/{filename}')}"


def copy_images(notes: list[dict], config: ImportConfig) -> dict[Path, dict[str, str]]:
    mapping: dict[Path, dict[str, str]] = {}
    images_root = config.docs_root / "images"
    if images_root.exists():
        shutil.rmtree(images_root)

    for note in notes:
        image_dir = note["path"].parent / "i"
        if not image_dir.is_dir():
            continue
        dest_dir = images_root / note["category"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        note_map: dict[str, str] = {}
        for image in image_dir.iterdir():
            if not image.is_file():
                continue
            dest = dest_dir / image.name
            shutil.copy2(image, dest)
            note_map[f"i/{image.name}"] = image_url(config, note["category"], image.name)
        mapping[note["path"]] = note_map
    return mapping


def rewrite_body(note: dict, uuid_to_url: dict[str, str], image_map: dict[str, str]) -> str:
    body = note["body"]
    body = strip_matching_h1(body, {note["title"], note["source_title"]})
    body = YOUTUBE_RE.sub(lambda match: youtube_embed(match.group(1)), body)

    def replace_image(match: re.Match[str]) -> str:
        alt, src = match.group(1), match.group(2)
        url = image_map.get(src)
        if not url:
            return match.group(0)
        return f"![{alt}]({url})"

    body = IMAGE_RE.sub(replace_image, body)

    def replace_link(match: re.Match[str]) -> str:
        label, uuid = match.group(1), match.group(2).upper()
        url = uuid_to_url.get(uuid)
        if not url:
            return f"{label} (page not published)"
        return f"[{label}]({url})"

    return NOTE_LINK_RE.sub(replace_link, body).rstrip() + "\n"


def write_page(note: dict, config: ImportConfig, body: str) -> None:
    dest = output_path(config.docs_root, note["category"], note["slug"], note["is_index"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    nav_order = note["order"][0] if note["order"][0] != 100 else 50
    front_matter = "\n".join(
        [
            "---",
            f"layout: {config.layout}",
            f"title: {yaml_escape(note['title'])}",
            f"category: {note['category']}",
            f"category_label: {yaml_escape(note['category_label'])}",
            f"nav_order: {nav_order}",
            f"permalink: {note['permalink']}",
            f"uuid: {note['uuid']}" if note["uuid"] else 'uuid: ""',
            "generated: true",
            "---",
            "",
        ]
    )
    dest.write_text(front_matter + body, encoding="utf-8")


def write_nav_data(notes: list[dict], config: ImportConfig) -> None:
    lines = ["# Generated by minknote-docs-import. Do not edit by hand.", "categories:"]
    seen: list[tuple[str, str]] = []
    for note in notes:
        pair = (note["category"], note["category_label"])
        if pair not in seen:
            seen.append(pair)

    for category, label in seen:
        lines.append(f"  - id: {category}")
        lines.append(f"    label: {yaml_escape(label)}")
        lines.append("    pages:")
        for note in notes:
            if note["category"] != category:
                continue
            lines.append(f"      - title: {yaml_escape(note['title'])}")
            lines.append(f"        url: {note['permalink']}")
    config.nav_data_file.parent.mkdir(parents=True, exist_ok=True)
    config.nav_data_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def is_generated_markdown(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    return len(parts) >= 3 and "generated: true" in parts[1]


def clear_generated_output(config: ImportConfig) -> None:
    if config.docs_root.exists():
        for path in config.docs_root.rglob("*.md"):
            if is_generated_markdown(path):
                path.unlink()

        images_root = config.docs_root / "images"
        if images_root.exists():
            shutil.rmtree(images_root)

    if config.nav_data_file.exists():
        config.nav_data_file.unlink()


def import_docs(config: ImportConfig) -> list[dict]:
    config.docs_root.mkdir(parents=True, exist_ok=True)
    clear_generated_output(config)

    notes = collect_notes(config)
    if not notes:
        raise SystemExit(f"No markdown notes found in {config.source}")

    uuid_to_url = {note["uuid"]: note["permalink"] for note in notes if note["uuid"]}
    image_maps = copy_images(notes, config)

    for note in notes:
        body = rewrite_body(note, uuid_to_url, image_maps.get(note["path"], {}))
        write_page(note, config, body)

    write_nav_data(notes, config)
    return notes


def relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        raise argparse.ArgumentTypeError("Expected a path relative to --site-root")
    return path


def normalise_base_url(value: str) -> str:
    return "/" + clean_url_part(value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("import",), help="Import or refresh generated Jekyll docs.")
    parser.add_argument("--source", required=True, help="Path to the MinkNote journal folder to export.")
    parser.add_argument("--site-root", required=True, help="Path to the Jekyll site root.")
    parser.add_argument(
        "--docs-path",
        default=Path("apps/minknote/docs"),
        type=relative_path,
        help="Generated docs path inside the Jekyll site.",
    )
    parser.add_argument(
        "--nav-data-path",
        default=Path("_data/minknote_docs.yml"),
        type=relative_path,
        help="Generated navigation YAML path inside the Jekyll site.",
    )
    parser.add_argument("--base-url", default="/apps/minknote/docs", help="Public URL prefix for generated docs.")
    parser.add_argument("--layout", default="minknote-docs", help="Jekyll layout for generated pages.")
    parser.add_argument(
        "--ignore",
        action="extend",
        default=[],
        nargs="+",
        help="One or more source filenames or source-relative glob patterns to skip.",
    )
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"Source folder does not exist: {source}")

    site_root = Path(args.site_root).expanduser().resolve()
    if not site_root.is_dir():
        raise SystemExit(f"Site root does not exist: {site_root}")

    config = ImportConfig(
        source=source,
        site_root=site_root,
        docs_path=args.docs_path,
        nav_data_path=args.nav_data_path,
        base_url=normalise_base_url(args.base_url),
        layout=args.layout,
        ignore=tuple(args.ignore),
    )
    notes = import_docs(config)
    print(f"Imported {len(notes)} docs pages from {source}")
    for note in notes:
        print(f"  {note['category_label']}: {note['title']} -> {note['permalink']}")


if __name__ == "__main__":
    main()
