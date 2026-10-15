"""Curated connections between published projects and our guides."""

from datetime import UTC, datetime

# Only these listings are covered by the guide; do not match all editor tools.
EDITOR_GUIDE_PROJECTS = frozenset({"bend2-lsp", "bend-2-for-vs-code-nuxyel"})
EDITOR_GUIDE_ADDED_AT = datetime(2026, 10, 13, tzinfo=UTC)

# Dated source correction; do not change the original publication/sort date.
KNOT_RELEASE_CORRECTED_AT = datetime(2026, 10, 14, tzinfo=UTC)

HTTP_SERVER_REPOSITORY = "https://github.com/iamsahilsonawane/bend2-http-server"
HTTP_SERVER_CHECKED_AT = datetime(2026, 10, 15, tzinfo=UTC)


def has_http_server_note(project):
    """Keep the source-specific check off unrelated or repurposed listings."""
    return project.slug == "bend-http-server" and project.repository_url == HTTP_SERVER_REPOSITORY
