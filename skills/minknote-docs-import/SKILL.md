---
name: minknote-docs-import
description: >-
  Export a MinkNote journal folder into a Jekyll documentation section.
  Converts MinkNote front matter, rewrites minknote:// links to web URLs, copies
  images, replaces YouTube shortcodes, and regenerates navigation data. Use when
  publishing or synchronising MinkNote-authored docs to a Jekyll site.
---

# MinkNote Docs Import

Use this skill when a user wants to publish a MinkNote journal folder as Jekyll documentation.

Treat the source journal as the canonical content. Do not hand-edit generated Markdown pages in the Jekyll site; change the MinkNote notes and run the importer again.

## Concept

The importer takes a target MinkNote journal folder and exports every supported Markdown note into a Jekyll docs section.

The script owns generated Markdown pages, copied images, and the navigation data file. The Jekyll layout, CSS, and `_config.yml` defaults are site setup work and are outside this skill.

## Run

Import or refresh the generated docs:

```bash
python3 .codex/skills/minknote-docs-import/scripts/import_docs.py import \
  --source "/path/to/MinkNote journal" \
  --site-root "/path/to/jekyll-site" \
  --ignore changelog.md roadmap.md
```

Use the installed path for the current agent. For Cursor this may be `.cursor/skills/minknote-docs-import/scripts/import_docs.py`; for Codex user-level installs this may be `~/.codex/skills/minknote-docs-import/scripts/import_docs.py`.

## Important Options

- `--source`: MinkNote journal folder to export.
- `--site-root`: Jekyll site root.
- `--docs-path`: generated docs path inside the site. Defaults to `apps/minknote/docs`.
- `--nav-data-path`: generated navigation data path inside the site. Defaults to `_data/minknote_docs.yml`.
- `--base-url`: generated docs URL prefix. Defaults to `/apps/minknote/docs`.
- `--layout`: Jekyll layout written into generated front matter. Defaults to `minknote-docs`.
- `--ignore`: one or more source filenames or source-relative glob patterns to skip. Nothing is ignored unless this option is passed.

## Modes

`import` is the only mode. It deletes previously generated Markdown pages, copied images, and navigation data, then regenerates the docs from the current MinkNote source. First import and later refreshes use the same command, so added, deleted, and changed source notes are reflected in the Jekyll output.

## What The Script Does

1. Reads every `.md` file under the source folder.
2. Skips only files matched by `--ignore`, when provided.
3. Maps folders to sidebar categories:
   - source root -> Getting Started
   - `HowTo/` -> HowTo
   - `Reference/` -> Reference
4. Writes Jekyll front matter with `layout`, `title`, `category`, `permalink`, `uuid`, and `generated`.
5. Rewrites `minknote://open/<uuid>` links to matching generated docs URLs.
6. Copies `i/` images into the generated docs image folder and rewrites image paths.
7. Replaces `{{youtube:VIDEO_ID}}` with a privacy-enhanced YouTube iframe.
8. Regenerates the configured navigation YAML file, such as `_data/minknote_docs.yml`.

## After Import

- Review the generated docs in the Jekyll site.
- Confirm the site navigation points at the generated docs `--base-url`.
- If site layout or `_config.yml` changes are needed, make those changes outside this skill.
