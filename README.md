# MinkNote Skills

Installable agent skills for MinkNote workflows.

## Install

Install a specific skill into Codex:

```bash
npx github:demianturner/minknote-skills install minknote-docs-import --agent codex
```

Install into a repository-local Cursor skills folder:

```bash
npx github:demianturner/minknote-skills install minknote-docs-import --agent cursor
```

Install into any skills folder:

```bash
npx github:demianturner/minknote-skills install minknote-docs-import --dest .cursor/skills
```

Replace an existing installed copy:

```bash
npx github:demianturner/minknote-skills install minknote-docs-import --agent codex --force
```

List available skills:

```bash
npx github:demianturner/minknote-skills list
```

## Skills

### minknote-docs-import

Exports a target MinkNote journal folder into a Jekyll documentation section. It converts note front matter, rewrites `minknote://open/<uuid>` links to generated web URLs, copies images, replaces YouTube shortcodes, and writes the navigation data file used by the Jekyll template. Root notes become Getting Started; each top-level journal folder becomes its own sidebar section.

The Jekyll layout, CSS, and `_config.yml` changes are intentionally out of scope. This skill assumes those site pieces already exist.

## Repository Layout

```text
skills/
  minknote-docs-import/
    SKILL.md
    scripts/
      import_docs.py
bin/
  minknote-skills.js
```

## Development

Run the importer directly from the repo while iterating:

```bash
python3 skills/minknote-docs-import/scripts/import_docs.py import \
  --source "/path/to/MinkNote journal" \
  --site-root "/path/to/jekyll-site" \
  --ignore changelog.md roadmap.md
```

Run the installer locally:

```bash
node bin/minknote-skills.js list
node bin/minknote-skills.js install minknote-docs-import --dest /tmp/minknote-skills-test --force
```
