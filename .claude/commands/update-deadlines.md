---
description: Monthly maintenance pass — verify predicted deadlines against official CFPs, add newly-announced editions, and refresh stale predictions.
allowed-tools: Bash, Read, Edit, Write, Glob, Grep, WebSearch, WebFetch
---

You are performing the **monthly maintenance pass** on the ai-deadlines dataset.
Read `.claude/CLAUDE.md` first for the data conventions — they are binding
(quoting rules, the "no bare `: ` in notes", the `Predicted` note format, and
the year N+1 rule).

Today's date is provided by the environment — treat it as "now" for all
"upcoming / past" judgements. Work only inside `_data/conferences/*.yml`.

## Goal

Keep the dataset accurate with **minimal, well-sourced** edits. Three jobs, in
order:

### 1. Verify & promote predicted entries
For every entry whose `note` starts with `Predicted` (or whose `deadline` is
`TBA`) and whose conference is still in the future:
- Find the official CFP. Prefer the conference's own domain; the existing
  `link` is the best starting guess. Use `WebSearch` for
  `"<TITLE> <year> call for papers"` then `WebFetch` the official page.
- If official dates are now published, **replace** the predicted values:
  set the real `deadline`, `abstract_deadline` (if any), `place`, `date`,
  `start`, `end`, and rewrite the `note` to describe the real key dates
  (drop the word `Predicted` so the card stops showing the predicted style).
  Update `link` to the year-specific official URL.
- If still unannounced, **re-estimate**: keep it `Predicted`, but refresh the
  estimate using the venue's most recent prior-year submission date and refresh
  the "past deadlines — …" reference list to the latest 3.

### 2. Add newly-announced next editions
- Run `python utils/find_missing_conferences.py` to list venues whose latest
  entry is stale. Treat it as a worklist, not gospel.
- For each, check the official site. **Only add edition N+1 once edition N has a
  confirmed (non-`TBA`, non-predicted) deadline** — per the year N+1 rule.
- If an official CFP exists, add a confirmed entry (newest-first in the file).
- If the next edition is plausible but unannounced and the rule allows it, add a
  `Predicted` entry anchored to history (same note format as the existing
  predicted entries).
- `utils/auto_add_conferences.py --dry-run` can draft entries, but **verify
  every field against the official source** before keeping it.

### 3. Sanity-check existing confirmed entries
- Flag (don't blindly change) any confirmed deadline already in the past for a
  conference still listed as upcoming — it may have been extended; check the
  source before editing.

## Rules
- **Never fabricate.** A date is either sourced from an official page (cite it in
  the `note` via the `More info <a …>here</a>` link) or clearly `Predicted` with
  its historical basis.
- Make the **smallest diff** that does the job — touch only the fields that
  changed. Do not reformat untouched entries or reorder fields.
- Respect every convention in `.claude/CLAUDE.md`, especially the no-bare-`: `
  rule inside notes.

## Validate (must pass before you finish)
```bash
ruby -ryaml -rdate -e 'Dir.glob("_data/conferences/*.yml").each{|f| YAML.safe_load(File.read(f),permitted_classes:[Date]) }; puts "YAML OK"'
bundle exec jekyll build
```
If either fails, fix it before concluding.

## Report
End with a concise summary, grouped as:
- **Promoted** (predicted → confirmed): venue, the official dates, source URL.
- **Added**: new editions and whether confirmed or predicted.
- **Re-estimated**: predictions refreshed, with old → new deadline.
- **Needs human review**: anything ambiguous, conflicting, or that you chose not
  to change — with the reason.

The git commit and PR are handled by the calling workflow; you only edit files
and produce this summary. If nothing needed changing, say so explicitly and make
no edits.
