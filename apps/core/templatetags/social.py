"""Consistent public share metadata for both site shells."""

from django import template
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import Truncator

from apps.directory.social import project_card_content, project_card_version
from apps.pages.services import build_absolute_public_url

register = template.Library()
DEFAULT_DESCRIPTION = (
    "Discover apps, games, tools, and experiments built with Bend 2. "
    "A human-reviewed directory with links to the builds and their sources."
)


@register.inclusion_tag("components/social_meta.html", takes_context=True)
def social_meta(context):
    request = context.get("request")
    route = getattr(getattr(request, "resolver_match", None), "url_name", "")
    title = "Built with Bend — A directory of Bend 2 projects"
    description = DEFAULT_DESCRIPTION
    card = "directory"
    kind = "website"
    image = ""
    alt = ""
    project = context.get("project")
    post = context.get("blog_post")
    if project:
        title = f"{project.title} — Built with Bend"
        description = Truncator(project.description).chars(200)
        version = project_card_version(project_card_content(project))
        image = build_absolute_public_url(
            reverse("directory:project_image", args=[project.slug]) + f"?v={version}"
        )
        alt = f"{project.title} — a project built with Bend 2"
    elif post:
        title, description = post.title, post.description
        image, alt = post.image_url, post.image_alt
        kind = "article"
        card = "blog"
    elif route == "blog_posts":
        title, description = context["blog_title"], context["blog_description"]
        card = "blog"
    elif route == "docs_page":
        title = f"{context['page_title']} — Built with Bend Guides"
        description = (
            context.get("meta_description") or f"{context['page_title']} for Built with Bend."
        )
        card = "guides"
    elif route in ("submit", "submitted"):
        title = "Submit a build — Built with Bend"
        description = (
            "Share your Bend 2 project with the community. Every submission is human-reviewed."
        )
        card = "submit"
    elif route in ("privacy_policy", "terms_of_service", "pricing"):
        titles = {
            "privacy_policy": "Privacy Policy",
            "terms_of_service": "Terms of Service",
            "pricing": "Sponsorship",
        }
        title = f"{titles[route]} — Built with Bend"
        description = f"{titles[route]} information for the Built with Bend project directory."
    image = image or build_absolute_public_url(static(f"social/{card}.png"))
    standard_images = {
        build_absolute_public_url(path)
        for name in ("directory", "blog", "guides", "submit", "bend-2-projects")
        for path in (static(f"social/{name}.png"), f"/static/social/{name}.png")
    }
    return {
        "title": title,
        "description": description,
        "url": context.get("canonical_url")
        or build_absolute_public_url(getattr(request, "path", "/")),
        "kind": kind,
        "image": image,
        "image_alt": alt or f"Built with Bend — {card.title()}",
        # Custom editorial images can have their own dimensions and format.
        "standard_image": bool(project) or image in standard_images,
    }
