from django.conf import settings

from .models import Page


def site(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        # Lazy queryset: only runs on templates that render the nav.
        "nav_pages": Page.objects.filter(is_published=True, show_in_nav=True),
    }
