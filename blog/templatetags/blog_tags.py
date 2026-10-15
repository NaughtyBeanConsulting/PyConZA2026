from django import template
from django.utils.safestring import mark_safe

from blog.models import clean_html

register = template.Library()


@register.filter
def sanitized(html):
    """Render stored rich text. It's cleaned on save; cleaning again here covers
    anything that reached the database another way (fixtures, raw SQL, updates)."""
    return mark_safe(clean_html(html))
