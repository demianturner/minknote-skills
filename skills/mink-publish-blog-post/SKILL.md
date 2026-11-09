---
name: mink-publish-blog-post
description: >-
  Publish a MinkNote markdown article as a dated post in a Jekyll blog section.
  Uses the article's `i/` image folder, optimises and copies images, writes the
  post front matter (title, date, description, hero-image, show-hero), installs
  the MinkNote blog Jekyll plugin when missing, and adds the post to llms.txt.
  Use when the user wants to publish, import, or add a MinkNote note to a blog.
---

# Publish Blog Post

Use this skill when a user wants to publish a MinkNote-authored Markdown article
as a blog post on a Jekyll site.

Treat the MinkNote article as the canonical content. The script owns the dated
post file, the copied blog images, the `_plugins/minknote_blog.rb` plugin when it
is missing, and the `llms.txt` entry. The Jekyll layout, CSS, and `_config.yml`
remain site setup work.

## Inputs

Collect these before running. Only the first three are required.

- **Article**: path to the MinkNote `.md` file.
- **Site root**: path to the Jekyll site.
- **Domain**: the site's public domain, for example `muse23.com`.
- **Blog path**: the blog section inside the site. Defaults to `apps/minknote/blog`.
- **Images**: the article's images. By default the script reads the `i/` folder
  next to the article, matching the `minknote://`-style `i/<file>` links in the body.
- **Hero image**: optional. Defaults to the article's first image.

## Run

Publish an article:

```bash
python3 .codex/skills/mink-publish-blog-post/scripts/publish_blog.py \
  --article "/path/to/Article.md" \
  --site-root "/path/to/jekyll-site" \
  --domain muse23.com \
  --blog-path apps/minknote/blog \
  --optimise-inline \
  --rename 'CleanShot_2026-11-08_at_11.26.56@2x-1.png=move-to-icloud-menu' \
  --rename 'CleanShot_2026-11-08_at_11.38.25@2x.png=icloud-projects'
```

Preview first with `--dry-run` — it reports the post path, URL, every image
conversion, the plugin, and the llms.txt change without writing anything:

```bash
python3 .codex/skills/mink-publish-blog-post/scripts/publish_blog.py \
  --article "/path/to/Article.md" --site-root "/path/to/jekyll-site" \
  --domain muse23.com --dry-run
```

Use the installed path for the current agent. For Cursor this may be
`.cursor/skills/mink-publish-blog-post/scripts/publish_blog.py`; for Codex user-level
installs this may be `~/.codex/skills/mink-publish-blog-post/scripts/publish_blog.py`.

## Options

- `--article`: path to the MinkNote markdown article. Required.
- `--site-root`: path to the Jekyll site root. Required.
- `--domain`: public blog domain. Required.
- `--blog-path`: blog section inside the site. Default `apps/minknote/blog`.
- `--blog-url-prefix`: public URL prefix for posts. Default `/<blog-path>`.
- `--images-url-prefix`: public URL prefix for images. Default `/<blog-path>/images`.
- `--layout`: Jekyll layout for the post. Default `minknote-post`.
- `--title` / `--slug` / `--description`: override values detected from the article.
- `--date`: publish date as `YYYY-MM-DD`. Defaults to today in the site timezone.
- `--timezone`: override the timezone. Defaults to the site `_config.yml` value.
- `--image-dir`: folder holding the images. Default `<article dir>/i`.
- `--hero-image`: source link or filename for the hero image.
- `--no-hero`: publish without a hero image.
- `--hero-format`: `jpeg` (default), `png`, or `keep`.
- `--jpeg-quality`: quality for conversions. Default `85`.
- `--max-width`: downscale images wider than this in pixels. `0` disables.
- `--optimise-inline`: convert large, non-transparent inline PNGs to JPEG.
- `--inline-threshold-kb`: minimum PNG size for `--optimise-inline`. Default `800`.
- `--rename SOURCE=DEST`: give an inline image a semantic output name. Repeatable.
- `--llms-section`: `llms.txt` section that lists posts. Default `MinkNote`.
- `--no-llms`: leave `llms.txt` untouched.
- `--force`: overwrite an existing post file.
- `--dry-run`: report changes without writing files.

## Optimising images

MinkNote pastes screenshots into an `i/` folder at full Retina resolution, so raw
PNGs are often 1–3 MB. The script uses the macOS `sips` tool to shrink them and
save them next to the artwork.

- The hero image is renamed to the post slug (`<slug>.jpg`) and converted to JPEG
  at `--jpeg-quality`. This keeps the URL readable and predictable.
- `--optimise-inline` converts large inline PNGs that have **no transparency** to
  JPEG, keeping screenshots light while preserving images such as logos or icons
  that rely on an alpha channel.
- `--max-width` downscales anything wider than the given pixel width.
- `--rename` gives an inline image a semantic filename instead of a raw
  screenshot name. Use it whenever the article's link points at a `CleanShot…`
  or similarly opaque filename.
- `sips` is macOS-only. On other platforms images are copied unchanged and the
  script reports it.

Typical results: a 1 MB iPad screenshot became 555 KB, and a 2.6 MB screenshot
became 348 KB.

## What the script does

1. Reads the article and its front matter, then derives the title (front matter,
   `--title`, or the first `#` heading; trailing `/v1` draft markers are removed).
2. Slugs the title and builds a dated filename, for example
   `2026-11-08-say-hello-to-iphone-and-ipad.md`.
3. Copies and optimises the `i/` images into `<blog-path>/images/`, giving the
   hero the post slug as its name.
4. Rewrites every `i/<file>` image link to an absolute blog image URL
   (`/apps/minknote/blog/images/...`), so links work from any page.
5. Removes the duplicate H1 when the body repeats the title, and expands
   `{{youtube:VIDEO_ID}}` shortcodes into privacy-enhanced embeds.
6. Writes front matter with `layout`, `title`, `date`, `description`, and, when a
   hero image is set, `hero-image` and `show-hero: true`.
7. Installs `_plugins/minknote_blog.rb` when missing, targeted at `--blog-path`.
   If the plugin exists but points elsewhere it is left untouched and a warning
   is printed.
8. Adds the post to `llms.txt` when the site has one, under the `--llms-section`
   heading (default `MinkNote`). Re-running updates the existing entry in place
   instead of duplicating it.

## Front matter

The script writes the front matter the blog layout expects:

```yaml
---
layout: minknote-post
title: "Say Hello to iPhone and iPad!"
date: 2026-11-08 09:30 +0000
description: A short summary for the blog index and social previews.
hero-image: say-hello-to-iphone-and-ipad.jpg
show-hero: true
---
```

- `hero-image` is the hero filename. The layout resolves a bare filename against
  `/apps/minknote/blog/images/` and accepts an absolute path or full URL too.
- `show-hero: true` renders the hero image above the title. Omit it or set
  `show-hero: false` to hide the hero.
- The plugin maps `hero-image`/`show-hero` to `hero_image`/`show_hero` and sets
  `minknote_blog: true` so the blog index can find the post.

## Images

Always reference blog images with absolute paths, for example:

```markdown
![The project switcher](/apps/minknote/blog/images/move-to-icloud-menu.jpg)
```

Absolute paths keep images working from the post page, the blog index, feeds,
and any future syndication. The script writes these paths for you; do not
hand-edit them to relative paths afterwards.

## The blog plugin

`_plugins/minknote_blog.rb` turns dated files in the blog folder into pages at
`<blog-url-prefix>/<slug>/`. It also marks each page for the blog index and maps
the `hero-image`/`show-hero` keys. The script installs it when missing. The
reference copy lives in `assets/minknote_blog.rb.txt`.

## Site setup

This skill assumes the Jekyll site already has the blog layout and CSS. The
reference pieces are in `assets/` if the site needs them:

- `assets/minknote-post.html` — the post layout.
- `assets/minknote-blog-index.html` — the blog index loop.
- `assets/minknote-blog-hero-src.html` — the hero path include.

## After publishing

- Review the new post in the Jekyll site and confirm it appears on the blog index.
- Confirm the images render and the hero shows above the title.
- If the site uses `llms.txt`, confirm the new entry sits under the right heading.
