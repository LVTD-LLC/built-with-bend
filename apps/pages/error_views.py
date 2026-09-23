from django.http import HttpResponseNotFound
from django.template.loader import render_to_string


def page_not_found(request, exception):
    """Keep missing pages and APPEND_SLASH redirects independent of the database."""
    # Passing request would run all context processors, including promotional
    # banner queries. Error rendering must also work with a closed connection.
    response = HttpResponseNotFound(render_to_string("404.html"))
    response["X-Robots-Tag"] = "noindex, follow"
    return response
