"""Curated connections between published projects and our guides."""

import json
from datetime import UTC, datetime

# Only these listings are covered by the guide; do not match all editor tools.
EDITOR_GUIDE_PROJECTS = frozenset({"bend2-lsp", "bend-2-for-vs-code-nuxyel"})
EDITOR_GUIDE_ADDED_AT = datetime(2026, 10, 13, tzinfo=UTC)

# Dated source correction; do not change the original publication/sort date.
KNOT_RELEASE_CORRECTED_AT = datetime(2026, 10, 14, tzinfo=UTC)
KNOT_FIRST_USE_REPOSITORY = "https://github.com/MatheusBBarni/knot-node-tooling"
KNOT_FIRST_USE_ADDED_AT = datetime(2026, 10, 28, tzinfo=UTC)

HTTP_SERVER_REPOSITORY = "https://github.com/iamsahilsonawane/bend2-http-server"
HTTP_SERVER_CHECKED_AT = datetime(2026, 10, 15, tzinfo=UTC)
HTTP_SERVER_DEMO_ADDED_AT = datetime(2026, 10, 22, tzinfo=UTC)

JENDHUB_REPOSITORY = "https://github.com/LeeeeT/JendHub"
JENDHUB_WEBSITE = "https://jend.leeeet.dev/"
JENDHUB_DESTINATIONS_RESTORED_AT = datetime(2026, 10, 17, tzinfo=UTC)

# The walkthrough uses these two discovery tools, not every package or tool.
PACKAGE_GUIDE_REPOSITORIES = {
    "jendhub": JENDHUB_REPOSITORY,
    "bend-packages": "https://github.com/777genius/bend-packages",
}
PACKAGE_GUIDE_ADDED_AT = datetime(2026, 10, 21, tzinfo=UTC)

BROWSER_EXERCISE_REPOSITORY = "https://github.com/raunak-11/bend-explainer"
BROWSER_EXERCISE_ADDED_AT = datetime(2026, 10, 23, tzinfo=UTC)

NEOVIM_FIRST_USE_REPOSITORY = "https://github.com/nuxyel/bend2-nvim"
NEOVIM_FIRST_USE_ADDED_AT = datetime(2026, 10, 27, tzinfo=UTC)


def has_neovim_first_use(project):
    return (
        project.slug == "bend-2-for-neovim"
        and project.repository_url == NEOVIM_FIRST_USE_REPOSITORY
    )


def has_browser_exercise(project):
    return (
        project.slug == "bend-explained" and project.repository_url == BROWSER_EXERCISE_REPOSITORY
    )


def has_package_guide(project):
    return bool(
        project.repository_url
        and PACKAGE_GUIDE_REPOSITORIES.get(project.slug) == project.repository_url
    )


def has_jendhub_destinations(project):
    return (
        project.slug == "jendhub"
        and project.repository_url == JENDHUB_REPOSITORY
        and project.website_url == JENDHUB_WEBSITE
    )


def has_http_server_note(project):
    """Keep the source-specific check off unrelated or repurposed listings."""
    return project.slug == "bend-http-server" and project.repository_url == HTTP_SERVER_REPOSITORY


def has_knot_first_use(project):
    return project.slug == "knot" and project.repository_url == KNOT_FIRST_USE_REPOSITORY


def pocket_workshop_metadata(project, site_url):
    """Describe only the reviewed browser app, never repurposed catalog rows."""
    if (
        project.slug != "bend-2-pocket-workshop"
        or project.repository_url != "https://github.com/np/bend-workshop"
        or project.website_url != "https://np.github.io/bend-workshop/"
    ):
        return None
    description = (
        "Try Bend 2 in a browser editor with examples and proof-hole goals. "
        "See checked first-use results, compiler version and kernel limits."
    )
    page_url = site_url.rstrip("/") + project.get_absolute_url()
    schema = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": project.title,
            "url": project.website_url,
            "sameAs": project.repository_url,
            "description": description,
            "applicationCategory": "DeveloperApplication",
            "operatingSystem": "Web browser",
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Built with Bend", "item": site_url},
                {"@type": "ListItem", "position": 2, "name": project.title, "item": page_url},
            ],
        },
    ]
    # JSON inside a script element must not let a catalog title close the tag.
    schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    return {"description": description, "schema_json": schema_json}
