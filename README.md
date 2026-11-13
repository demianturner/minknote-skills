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

For example, install the blog post publisher:

```bash
npx github:demianturner/minknote-skills install mink-publish-blog-post --agent codex
```

## Skills

Two skills publish MinkNote content to a Jekyll site. They share the same
assumptions but do different jobs:

| Skill | What it publishes | Source input | Output |
| --- | --- | --- | --- |
| `mink-publish-blog-post` | One blog post | A single MinkNote article plus its `i/` images | A dated post in the blog section |
| `mink-publish-documentation` | A whole docs section | A MinkNote journal folder | A set of pages plus sidebar navigation |

**Shared assumptions.** Both skills are Jekyll-only and expect an existing site:
a Jekyll install, a layout for the target section, and the site's CSS. They
transform Markdown, copy images, and write front matter; they do not create the
Jekyll site itself.

### mink-publish-blog-post

Publishes a MinkNote markdown article as a dated post in a Jekyll blog section.
It derives the title, slug, and date, copies and optimises the article's `i/`
images with macOS `sips`, rewrites image links to absolute blog paths, writes the
post front matter (`hero-image`, `show-hero`), installs the
`_plugins/minknote_blog.rb` plugin when missing, and adds the post to `llms.txt`
when the site has one. Supports `--dry-run` and idempotent re-runs.

Expects a `minknote-post` layout and a blog index that lists pages marked
`minknote_blog`. Reference layout files are bundled in the skill's `assets/`
folder.

### mink-publish-documentation

Exports a target MinkNote journal folder into a Jekyll documentation section. It
converts note front matter, rewrites `minknote://open/<uuid>` links to generated
web URLs, copies images, replaces YouTube shortcodes, and writes the navigation
data file used by the Jekyll template. Root notes become Getting Started; each
top-level journal folder becomes its own sidebar section.

Expects a `minknote-docs` layout and a docs sidebar that reads the generated
navigation YAML.

### mink-download-reddit-posts

Imports Reddit post bookmarks from a selected Raindrop collection into category folders as MinkNote Markdown notes. Re-running refreshes existing notes while preserving their UUIDs. Raindrop tags are used for folder selection and are not written into notes.

## Repository Layout

Each folder under `skills/` is one installable skill, copied as a unit to the
chosen skills directory:

```text
skills/
  mink-publish-blog-post/       # one blog post -> blog section
    SKILL.md
    assets/                     # reference Jekyll layout files
      minknote-post.html
      minknote-blog-index.html
      minknote-blog-hero-src.html
      minknote_blog.rb.txt
    scripts/
      publish_blog.py
  mink-publish-documentation/   # journal folder -> docs section
    SKILL.md
    scripts/
      import_docs.py
bin/
  minknote-skills.js            # installer
```

`assets/` files are reference copies for site setup; the skill scripts do not
read them at run time.

## Development

Run the blog post publisher directly from the repo while iterating:

```bash
python3 skills/mink-publish-blog-post/scripts/publish_blog.py \
  --article "/path/to/Article.md" \
  --site-root "/path/to/jekyll-site" \
  --domain muse23.com \
  --dry-run
```

Run the documentation publisher directly from the repo:

```bash
python3 skills/mink-publish-documentation/scripts/import_docs.py import \
  --source "/path/to/MinkNote journal" \
  --site-root "/path/to/jekyll-site" \
  --ignore changelog.md roadmap.md
```

Run the installer locally:

```bash
node bin/minknote-skills.js list
node bin/minknote-skills.js install mink-publish-blog-post --dest /tmp/minknote-skills-test --force
```
