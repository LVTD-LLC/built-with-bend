"""Curated connections between published projects and our guides."""

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
