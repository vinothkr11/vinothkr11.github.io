---
layout: archive
title: "CV"
permalink: /cv/
author_profile: true
redirect_from:
  - /resume
---

{% include base_path %}

## Education

- **Ph.D.** in [Your Field], [Your University], [Year]
- **M.Sc.** in [Your Field], [Your University], [Year]
- **B.Sc.** in [Your Field], [Your University], [Year]

## Research Experience

- **Post Doctoral Fellow**, [Lab/Institute], Toronto, Canada (Present)
  - Research focus: [describe your current research]

- **[Previous Role]**, [Institution], [Location] ([Years])
  - [Brief description of responsibilities]

## Skills

- [Technique/Method 1]
- [Technique/Method 2]
- [Programming Language / Software]
- [Other relevant skills]

## Publications

  <ul>{% for post in site.publications reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>

## Talks

  <ul>{% for post in site.talks reversed %}
    {% include archive-single-talk-cv.html %}
  {% endfor %}</ul>

## Teaching

  <ul>{% for post in site.teaching reversed %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>

## Awards & Honors

- [Award Name], [Organization], [Year]
- [Fellowship/Scholarship], [Organization], [Year]
