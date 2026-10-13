"""Curated connections between published projects and our guides."""

from datetime import UTC, datetime

# Only these listings are covered by the guide; do not match all editor tools.
EDITOR_GUIDE_PROJECTS = frozenset({"bend2-lsp", "bend-2-for-vs-code-nuxyel"})
EDITOR_GUIDE_ADDED_AT = datetime(2026, 10, 13, tzinfo=UTC)
