"""Source-checked Bend 2 discovery without removing the category browse ring."""

from datetime import UTC, datetime

from django.db.models import Q

# Positive, reviewed identities only. An absent entry means unclassified, not
# classic Bend or incompatible. Pinned primary evidence: docs/seo/related-projects.md.
BEND2_PROJECTS = {
    "bend-2-pocket-workshop": "https://github.com/np/bend-workshop",
    "bend-2-for-neovim": "https://github.com/nuxyel/bend2-nvim",
    "bend-2-for-vs-code-nuxyel": "https://github.com/nuxyel/bend2-vscode",
    "bend2-lsp": "https://github.com/don2e4/bend2-lsp",
    "jendhub": "https://github.com/LeeeeT/JendHub",
    "knot": "https://github.com/MatheusBBarni/knot-node-tooling",
}
BEND2_DISCOVERY_ADDED_AT = datetime(2026, 10, 31, tzinfo=UTC)


def has_bend2_discovery(project):
    return bool(
        project.repository_url and BEND2_PROJECTS.get(project.slug) == project.repository_url
    )


def category_ring(siblings, slug, limit=3):
    """Walk by slug and wrap, independently of popularity or publication date."""
    result = list(siblings.filter(slug__gt=slug)[:limit])
    if len(result) < limit:
        result.extend(siblings.filter(slug__lt=slug)[: limit - len(result)])
    return result


def related_projects(project, siblings):
    ring = category_ring(siblings, project.slug)
    if not ring or not has_bend2_discovery(project):
        return ring

    reviewed = Q()
    for slug, repository in BEND2_PROJECTS.items():
        reviewed |= Q(slug=slug, repository_url=repository)
    # Always retain the next category sibling: every published member keeps an
    # inbound browse path, including classic and unclassified builds. Use the
    # other two slots for reviewed Bend 2 peers of the same project type.
    next_sibling = ring[0]
    peers = category_ring(siblings.filter(reviewed).exclude(pk=next_sibling.pk), project.slug, 2)
    selected = peers + [next_sibling]
    seen = {item.pk for item in selected}
    for item in ring[1:]:
        if len(selected) == 3:
            break
        if item.pk not in seen:
            selected.append(item)
            seen.add(item.pk)
    return selected
