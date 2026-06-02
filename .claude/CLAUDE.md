# ai-deadlines — repo guide for Claude

A Jekyll static site of countdown timers to top AI/ML/CV/NLP/RO/SP conference
submission deadlines. Published via **GitHub Pages from the `gh-pages` branch**
(which is also the default branch). Live at https://mlciv.com/ai-deadlines.

## Where the data lives

- `_data/conferences/*.yml` — one file per venue (e.g. `emnlp.yml`, `cvpr.yml`).
  Each file is a YAML **list**, newest edition first. One list item = one
  conference edition.
- `_data/types.yml` — maps subject names to the short `sub` tags (`ML`, `CV`,
  `NLP`, `RO`, `SP`, `DM`, `AP`, `KR`, `HCI`, `EDU`, `CG`).
- The site, a per-subject API, and `conferences.json` are generated at build
  time by `_plugins/api_json_generator.rb`. You only ever edit the YAML.

## Entry schema

Required: `title`, `year`, `id`, `link`, `deadline`, `timezone`, `date`,
`place`, `sub`. Optional: `abstract_deadline`, `note`, `hindex`, `full_name`,
`start`, `end`, `paperslink`, `pwclink`.

```yaml
- title: EMNLP
  year: 2026
  id: emnlp26            # title lowercased + last two digits of the year
  link: https://2026.emnlp.org/
  deadline: '2026-05-25 23:59:00'   # quote it; or the literal: TBA
  timezone: UTC-12        # AoE deadlines use UTC-12; else a moment-tz string
  place: TBA
  date: October 24-29, 2026
  start: '2026-10-24'
  end: '2026-10-29'
  sub:
  - NLP
  note: All submissions via ARR. More info <a href='https://2026.emnlp.org/'>here</a>.
```

## Conventions that matter

- **Quote `deadline` / `start` / `end`** so they stay strings, not YAML dates.
  Unconfirmed deadline is the literal `TBA`.
- **`note` is an unquoted scalar — never put a bare `": "` (colon-space) inside
  it**, it breaks the YAML parser. Use an em dash or comma instead. The note may
  contain `<a href='…'>…</a>` (single quotes inside are fine when unquoted).
- **Predicted entries**: when a deadline is an estimate (no official CFP yet),
  the `note` must **start with the word `Predicted`** — the card template
  (`index.html`) keys off that to apply distinct styling. Pattern in use:
  `Predicted deadline based on historical <TITLE> pattern (past deadlines — <y1 date>, <y2 date>, <y3 date>). Please verify on the official conference website. More info <a href='<link>'>here</a>.`
- **Year N+1 rule**: do not add/predict edition N+1 until edition N exists with a
  **confirmed, non-`TBA`, non-predicted** deadline.
- **AoE** ("anywhere on earth") maps to `timezone: UTC-12`.
- **Never fabricate** a deadline. Either cite an official source or label it
  Predicted with the historical basis.

## Validate before committing

```bash
# every file must parse (dates appear as YAML Date objects — permit them)
ruby -ryaml -rdate -e 'Dir.glob("_data/conferences/*.yml").each{|f| YAML.safe_load(File.read(f),permitted_classes:[Date]) }; puts "YAML OK"'

# full build must succeed
bundle exec jekyll build
```

## Existing tooling (reuse, don't reinvent)

- `utils/find_missing_conferences.py` — lists venues whose latest entry is stale.
- `utils/auto_add_conferences.py [--dry-run] [--conference NAME]` — searches for
  CFPs and drafts new entries. Treat its output as a **draft to verify**, not
  ground truth.
- `.cursor/skills/query-deadlines-by-keyword/SKILL.md` — the published agent
  skill describing the same data model.

## Monthly maintenance

The `/update-deadlines` command (`.claude/commands/update-deadlines.md`) encodes
the recurring maintenance pass. `.github/workflows/monthly-update.yml` runs it
on a schedule and opens a PR against `gh-pages`.
