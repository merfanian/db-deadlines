---
layout: null
permalink: /api/
---
{
  "name": "AI Conference Deadlines API",
  "version": "1.0",
  "description": "Machine-readable JSON endpoints for AI conference deadlines",
  "endpoints": {
    "all_conferences": "{{ site.url }}{{ site.baseurl }}/conferences.json",
    "upcoming": "{{ site.url }}{{ site.baseurl }}/api/upcoming.json",
    "by_subject": {
      "ML":  "{{ site.url }}{{ site.baseurl }}/api/ML.json",
      "CV":  "{{ site.url }}{{ site.baseurl }}/api/CV.json",
      "NLP": "{{ site.url }}{{ site.baseurl }}/api/NLP.json",
      "RO":  "{{ site.url }}{{ site.baseurl }}/api/RO.json",
      "SP":  "{{ site.url }}{{ site.baseurl }}/api/SP.json",
      "DM":  "{{ site.url }}{{ site.baseurl }}/api/DM.json",
      "AP":  "{{ site.url }}{{ site.baseurl }}/api/AP.json",
      "KR":  "{{ site.url }}{{ site.baseurl }}/api/KR.json",
      "HCI": "{{ site.url }}{{ site.baseurl }}/api/HCI.json",
      "EDU": "{{ site.url }}{{ site.baseurl }}/api/EDU.json",
      "CG":  "{{ site.url }}{{ site.baseurl }}/api/CG.json"
    },
    "skill_descriptor": "https://raw.githubusercontent.com/{{ site.github_username }}/{{ site.github_repo }}/gh-pages/static/skill/SKILL.md",
    "ics_feed": "{{ site.url }}{{ site.baseurl }}/ai-deadlines.ics"
  },
  "fields": ["title", "year", "id", "full_name", "link", "deadline", "abstract_deadline", "timezone", "place", "date", "start", "end", "sub", "note", "hindex", "paperslink", "pwclink"],
  "subject_tags": {
    "ML":  "Machine Learning",
    "CV":  "Computer Vision",
    "NLP": "Natural Language Processing",
    "RO":  "Robotics",
    "SP":  "Speech",
    "DM":  "Data Mining",
    "AP":  "Planning / Autonomous Agents",
    "KR":  "Knowledge Representation",
    "HCI": "Human-Computer Interaction",
    "EDU": "AI in Education",
    "CG":  "Computer Graphics"
  },
  "source_repo": "https://github.com/{{ site.github_username }}/{{ site.github_repo }}"
}
