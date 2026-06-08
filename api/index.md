---
layout: null
permalink: /api/
---
{
  "name": "DB Conference Deadlines API",
  "version": "1.0",
  "description": "Machine-readable JSON endpoints for Database/Data Mining/IR/ML/Theory conference deadlines",
  "endpoints": {
    "all_conferences": "{{ site.url }}{{ site.baseurl }}/conferences.json",
    "upcoming": "{{ site.url }}{{ site.baseurl }}/api/upcoming.json",
    "by_subject": {
      "DB":  "{{ site.url }}{{ site.baseurl }}/api/DB.json",
      "DM":  "{{ site.url }}{{ site.baseurl }}/api/DM.json",
      "IR":  "{{ site.url }}{{ site.baseurl }}/api/IR.json",
      "ML":  "{{ site.url }}{{ site.baseurl }}/api/ML.json",
      "NLP": "{{ site.url }}{{ site.baseurl }}/api/NLP.json",
      "TH":  "{{ site.url }}{{ site.baseurl }}/api/TH.json"
    },
    "skill_descriptor": "https://raw.githubusercontent.com/{{ site.github_username }}/{{ site.github_repo }}/gh-pages/static/skill/SKILL.md",
    "ics_feed": "{{ site.url }}{{ site.baseurl }}/db-deadlines.ics"
  },
  "fields": ["title", "year", "id", "full_name", "link", "deadline", "abstract_deadline", "timezone", "place", "date", "start", "end", "sub", "note", "hindex", "paperslink", "pwclink"],
  "subject_tags": {
    "DB":  "Databases",
    "DM":  "Data Mining",
    "IR":  "Information Retrieval",
    "ML":  "Machine Learning",
    "NLP": "Natural Language Processing",
    "TH":  "Theory"
  },
  "source_repo": "https://github.com/{{ site.github_username }}/{{ site.github_repo }}"
}
