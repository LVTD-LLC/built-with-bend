# Guide version check — October 9, 2026

The existing guide now helps readers distinguish older HVM-based tutorials from
Bend 2 before choosing a project. Its title, description, URL, five project
examples, and newsletter form are unchanged.

The example was executed twice independently with Bend 2.0.35 and printed `42`.
Its syntax and execution behavior are linked to the version-pinned official guide.
This does not establish GPU support or compatibility of a larger application.

The screenshots show the actual Django-rendered preview at 390 and 1440 CSS pixels,
in light and dark themes. The code is readable without horizontal page overflow.
They are preview evidence, not proof of production deployment.

Checks: 435 local tests and 9 subtests passed; frontend lint/build, source-link
checks, BlogPosting JSON parsing, and source/rendered claim checks passed.
Independent content review covered accuracy, information gain, voice, structure,
and extractability. The incorrect installation anchor found in review was fixed.
No new test mirrors this reversible prose change; existing application tests cover
the Markdown route and metadata behavior.

Research and measurement history remain in the existing private store referenced
by `.seo/config.json`. No private analytics data is included here.
