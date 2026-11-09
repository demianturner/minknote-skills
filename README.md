# MinkNote Skills

Installable agent skills for MinkNote workflows.

## Install

Install a specific skill into Codex:

```bash
npx github:demianturner/minknote-skills install <skill> --agent codex
```

Install into a repository-local Cursor skills folder:

```bash
npx github:demianturner/minknote-skills install <skill> --agent cursor
```

Install into any skills folder:

```bash
npx github:demianturner/minknote-skills install <skill> --dest .cursor/skills
```

Replace an existing installed copy:

```bash
npx github:demianturner/minknote-skills install <skill> --agent codex --force
```

List available skills:

```bash
npx github:demianturner/minknote-skills list
```

Install every skill:

```bash
npx github:demianturner/minknote-skills install all --agent codex
```

For example, install the blog publisher:

```bash
npx github:demianturner/minknote-skills install publish-to-blog --agent codex
```

## Skills

### publish-to-blog

Publishes a MinkNote markdown article as a dated post in a Jekyll blog section. It derives the title, slug, and date, copies and optimises the article's `i/` images with macOS `sips`, rewrites image links to absolute blog paths, writes the post front matter (`hero-image`, `show-hero`), installs the `_plugins/minknote_blog.rb` plugin when missing, and adds the post to `llms.txt` when the site has one. Supports `--dry-run` and idempotent re-runs.

Assumes a Jekyll blog with a blog section, a `minknote-post` layout, and a blog index that lists pages marked `minknote_blog`. Reference layout files are bundled in the skill's `assets/` folder.

### publish-to-jekyll

Formerly `minknote-docs-import`.

Exports a target MinkNote journal folder into a Jekyll documentation section. It converts note front matter, rewrites `minknote://open/<uuid>` links to generated web URLs, copies images, replaces YouTube shortcodes, and writes the navigation data file used by the Jekyll template. Root notes become Getting Started; each top-level journal folder becomes its own sidebar section.

The Jekyll layout, CSS, and `_config.yml` changes are intentionally out of scope. This skill assumes those site pieces already exist.

## Repository Layout

```text
skills/
  publish-to-blog/
    SKILL.md
    assets/
      minknote-post.html
      minknote-blog-index.html
      minknote-blog-hero-src.html
      minknote_blog.rb.txt
    scripts/
      publish_blog.py
  publish-to-jekyll/
    SKILL.md
    scripts/
      import_docs.py
bin/
  minknote-skills.js
```

## Development

Run the blog publisher directly from the repo while iterating:

```bash
python3 skills/publish-to-blog/scripts/publish_blog.py \
  --article "/path/to/Article.md" \
  --site-root "/path/to/jekyll-site" \
  --domain muse23.com \
  --dry-run
```

Run the docs publisher directly from the repo:

```bash
python3 skills/publish-to-jekyll/scripts/import_docs.py import \
  --source "/path/to/MinkNote journal" \
  --site-root "/path/to/jekyll-site" \
  --ignore changelog.md roadmap.md
```

Run the installer locally:

```bash
node bin/minknote-skills.js list
node bin/minknote-skills.js install publish-to-blog --dest /tmp/minknote-skills-test --force
```
