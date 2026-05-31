---
layout: null
permalink: /static/skill/SKILL.html
name: query-deadlines-by-keyword
description: >-
  Answers conference submission deadline questions from topic keywords or research ideas.
  Works with a YAML conference dataset (Jekyll-style) or with web search alone. Maps natural
  language to subject tags (ML, CV, NLP, RO, etc.), ranks by upcoming deadlines, and flags
  predicted or unconfirmed dates. Use when the user asks for deadlines by topic, field, keyword,
  or vague research area, or for potential or next-year submission dates.
---

# Query deadlines by keyword or idea (portable)

## Published copy (for agents)

This file is deployed with the **AI Conference Deadlines** site. Agents may **fetch** the **source** markdown from GitHub (same text as in this repository):

- **Raw `SKILL.md` (for agents):** `https://raw.githubusercontent.com/mlciv/ai-deadlines/gh-pages/static/skill/SKILL.md`  
  (Replace `mlciv/ai-deadlines` with your fork’s `user/repo` if needed.)

**Human-readable page (built by Jekyll):** `/ai-deadlines/static/skill/SKILL.html` on the site.

Dataset backing this deployment (when applicable): conference YAML under `_data/conferences/` and `_data/types.yml` in the [source repository](https://github.com/mlciv/ai-deadlines).

## JSON API endpoints (machine-readable, no scraping required)

These endpoints are generated at build time and served as static JSON files.

| Endpoint | Description |
|---|---|
| `/ai-deadlines/conferences.json` | **All** conferences as a flat JSON array |
| `/ai-deadlines/api/` | API index with endpoint URLs and field documentation |
| `/ai-deadlines/api/upcoming.json` | Conferences with a concrete (non-TBA) deadline |
| `/ai-deadlines/api/ML.json` | Machine Learning conferences |
| `/ai-deadlines/api/CV.json` | Computer Vision conferences |
| `/ai-deadlines/api/NLP.json` | NLP conferences |
| `/ai-deadlines/api/RO.json` | Robotics conferences |
| `/ai-deadlines/api/SP.json` | Speech conferences |
| `/ai-deadlines/api/DM.json` | Data Mining conferences |
| `/ai-deadlines/api/AP.json` | Planning / Autonomous Agents |
| `/ai-deadlines/api/KR.json` | Knowledge Representation |
| `/ai-deadlines/api/HCI.json` | HCI conferences |
| `/ai-deadlines/api/EDU.json` | AI in Education |
| `/ai-deadlines/api/CG.json` | Computer Graphics |
| `/ai-deadlines/ai-deadlines.ics` | iCalendar feed (subscribe in Google/Apple Calendar) |

**Recommended agent workflow:**
1. Fetch `conferences.json` or a subject endpoint (e.g. `NLP.json`) — no HTML scraping needed.
2. Sort entries by the `deadline` field (ISO datetime string + `timezone`).
3. Flag entries whose `note` contains "Predicted" as unconfirmed — verify via the official `link`.
4. Use the `/api/` index JSON to discover current endpoint URLs programmatically.

## Audience

This file is **agent-agnostic**: any assistant (Cursor, OpenClaw, CLI agents, IDE plugins, etc.) can follow it if the instructions are **loaded into context** or **referenced as a skill URL**. No editor-specific APIs are required.

## Goal

Produce **accurate, sourced** answers to: “What conferences / deadlines match this keyword or idea?”

Use **either or both**:

1. **Structured data** — YAML files listing conferences (see [Data layout](#data-layout)).
2. **Web search** — official call-for-papers (CFP) pages when data is missing, predicted, or stale.

Never fabricate deadlines.

## Data layout (when a repo or dataset exists)

Typical **ai-deadlines–style** trees:

- `types.yml` (or equivalent): maps human-readable area names to short codes (`sub`), e.g. `ML`, `CV`, `NLP`.
- `conferences/*.yml` (or `_data/conferences/*.yml`): one or more YAML documents per file; each **conference** is a list item with fields such as:

  `title`, `year`, `id`, `link`, `deadline`, `abstract_deadline`, `timezone`, `place`, `date`, `start`, `end`, `sub`, `note`.

If the user’s workspace has no such paths, **skip file search** and rely on [Web-only mode](#web-only-mode).

**Convention:** `sub` may be a string or a list. Match if **any** tag fits the user’s topic.

## Subject tags (`sub`)

Map user language to tags using the project’s types file when present; otherwise use this table:

| User might say | Typical `sub` |
|----------------|-----------------|
| machine learning, deep learning | `ML` |
| computer vision, images, video | `CV` |
| NLP, LLMs, ACL-style | `NLP` |
| robotics, embodied | `RO` |
| speech, audio | `SP` |
| data mining, recsys | `DM` |
| planning | `AP` |
| knowledge representation | `KR` |
| HCI | `HCI` |
| AI + education | `EDU` |
| graphics | `CG` |

For narrow topics, also search **`title`**, **`full_name`**, and **`note`** text (e.g. “dialogue”, “3D”, “medical”).

## Workflow

1. **Normalize the query**  
   Extract 1–3 keywords; assign one or more `sub` values. If ambiguous, ask one short question or cover the most likely tags.

2. **Search structured data (if available)**  
   Grep or search all conference YAML for matching `sub:` and optional text fields. Respect the workspace root the user provides.

3. **Collect fields**  
   Per match: `title`, `year`, `id`, `deadline`, `abstract_deadline`, `timezone`, `place`, `date`, `link`, `note`.

4. **Sort by urgency**  
   Prefer deadlines **after** “today” (use user-provided or system date). Sort by main submission deadline unless only abstract/ARR dates exist—then state that clearly.

5. **Flag uncertainty**  
   If `note` (or absence of official link) suggests **Predicted**, **Estimated**, **TBA**, or **when available**, label the row **unconfirmed** and recommend the official CFP URL or a search: `"[conference acronym] [year] call for papers"`.

6. **Year-by-year predictions**  
   Do **not** predict or add year **N+1** until year **N** is ready: the entry must exist with a confirmed (non-predicted) deadline—not TBA/TBD. If 2026 is missing or unconfirmed, do not predict 2027.

7. **Web verification**  
   For unconfirmed rows or user requests for “latest” dates, open official domains (conference or society site) and reconcile with YAML.

## Web-only mode

If there is **no** local YAML:

1. Infer venues from keywords (e.g. vision → CVPR/ICCV/ECCV; ML → NeurIPS/ICML/ICLR; NLP → ACL/EMNLP/NAACL).
2. Use web search for **current year and next year** CFP pages.
3. Present deadlines with **source URL**; prefer pages hosted by the conference or ACM/IEEE/CVF as appropriate.

## Output format

Use a compact table or bullets:

- Conference (year)  
- Deadlines (abstract + full if both exist) and timezone  
- Venue / conference dates (short)  
- CFP or home link  
- **Confidence:** `official dataset` | `official web` | `predicted / unconfirmed`

## Examples

- **“Vision + multimodal deadlines”** → tags `CV` (+ `NLP` if needed); grep multimodal/MM; sort by date.  
- **“Spoken dialogue”** → grep dialogue/speech; include `NLP` and `SP` venues from data or web.  
- **“NeurIPS-style next cycle”** → `ML` venues; separate **official** vs **predicted** in notes.

## Loading this skill in other agents

- **HTTPS (raw markdown):** Fetch the raw GitHub URL for `static/skill/SKILL.md` and inject the response into context.  
- **Repository:** Clone the repo and read `static/skill/SKILL.md` (or `.cursor/skills/query-deadlines-by-keyword/SKILL.md` if present).  
- **Content:** The agent may use the markdown **body** (after the first YAML front matter block); the `name` and `description` fields help discovery where supported.  
- **Repo coupling:** When this skill ships **inside** a clone of ai-deadlines, default data paths are `_data/types.yml` and `_data/conferences/*.yml`. When used **standalone**, ignore those paths and use [Web-only mode](#web-only-mode) or ask the user for their dataset root.

## Display notes

Strip HTML from `note` when speaking plain text to the user. Sorting in a static site UI may differ from agent-side date sorting; always compute order from parsed deadline strings and timezone when possible.
