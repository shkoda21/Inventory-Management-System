"""
Custom template tag: {% query_string page=N %}

Rebuilds the current query string replacing (or adding) the given key=value
pair and removing any duplicate keys. Solves the paginator bug where
?page=3&page=2&... accumulates across clicks.

Usage in template:
    {% load pagination_tags %}
    <a href="?{% query_string page=page_obj.next_page_number %}">›</a>
    <a href="?{% query_string page=num %}">{{ num }}</a>
"""

from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    """
    Returns a URL-encoded query string based on the current request's
    GET parameters, with the supplied kwargs overriding or adding values.

    Example:
        Current URL:  ?q=vodka&capacity=2&page=2
        {% query_string page=3 %}  →  q=vodka&capacity=2&page=3
    """
    return params.urlencode()