from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify

from blog.models import Category, Page, Post, Tag

CATEGORIES = {
    "django": "Django",
    "frontend": "Front-end",
    "deployment": "Deployment",
}

TAGS = {
    "htmx": "htmx",
    "alpinejs": "alpinejs",
    "tailwind": "tailwind",
    "postgres": "postgres",
    "admin": "admin",
}

POSTS = [
    {
        "title": "Welcome to the blog",
        "category": "django",
        "tags": ["admin"],
        "excerpt": "What this demo blog is, and how the pieces fit together.",
        "body": (
            "<p>This is a small CMS blog built with <strong>Django</strong>, <strong>htmx</strong>, "
            "<strong>Alpine.js</strong>, <strong>Tailwind CSS</strong> and <strong>Postgres</strong>.</p>"
            "<h2>Editing content</h2>"
            "<p>Everything you see here is managed in the Django admin, styled with Django Unfold. "
            "Posts can be drafts, published, or scheduled for a future date.</p>"
            "<blockquote>Staff can preview drafts on the live site before publishing.</blockquote>"
        ),
    },
    {
        "title": "Search as you type with htmx",
        "category": "frontend",
        "tags": ["htmx"],
        "body": (
            "<p>The search box on the post list sends a request 300 ms after you stop typing. "
            "Django returns just the post cards, rendered from a template partial, and htmx swaps them in.</p>"
            "<pre>hx-get=\"/\" hx-trigger=\"input changed delay:300ms\" hx-target=\"#post-results\"</pre>"
            "<p>Without JavaScript it is still an ordinary GET form.</p>"
        ),
    },
    {
        "title": "Load more without a SPA",
        "category": "frontend",
        "tags": ["htmx"],
        "body": (
            "<p>The <em>Load more posts</em> link replaces itself with the next page of cards, "
            "plus a new link if there are more. One template partial serves both the first page and every page after it.</p>"
        ),
    },
    {
        "title": "Sprinkles of Alpine.js",
        "category": "frontend",
        "tags": ["alpinejs"],
        "body": (
            "<p>Alpine handles the small interactive bits: the mobile menu, the dark-mode toggle "
            "(remembered in your browser) and the copy-link button at the end of each post.</p>"
            "<ul><li>No build step for the JavaScript</li><li>State lives in the HTML</li>"
            "<li>Plays nicely with htmx swaps</li></ul>"
        ),
    },
    {
        "title": "Tailwind CSS v4 in a Django project",
        "category": "frontend",
        "tags": ["tailwind"],
        "body": (
            "<p>Tailwind scans the Django templates and writes one minified stylesheet to "
            "<code>static/dist/app.css</code>. Long-form content uses the typography plugin's "
            "<code>prose</code> classes, so headings, lists and quotes look right out of the box.</p>"
        ),
    },
    {
        "title": "A custom user model on day one",
        "category": "django",
        "tags": ["admin"],
        "body": (
            "<p>Users sign in with their email address; there is no username field at all. "
            "Swapping the user model later is painful, so it is done before the first migration.</p>"
        ),
    },
    {
        "title": "Static files with WhiteNoise",
        "category": "deployment",
        "tags": ["postgres"],
        "body": (
            "<p>In production WhiteNoise serves content-hashed, Brotli- and gzip-compressed static files "
            "straight from gunicorn, with far-future cache headers. No separate static file server needed.</p>"
        ),
    },
]

ABOUT = (
    "<p>This blog is a demo CMS for PyCon ZA 2026. Pages like this one are edited in the admin "
    "under <em>Pages</em> and appear in the top navigation.</p>"
)


class Command(BaseCommand):
    help = "Create demo categories, tags, posts and an About page. Safe to run more than once."

    def add_arguments(self, parser):
        parser.add_argument("--author", help="Email of the post author (default: the first superuser).")

    def handle(self, *args, **options):
        author = self.get_author(options["author"])

        categories = {
            slug: Category.objects.get_or_create(slug=slug, defaults={"name": name})[0]
            for slug, name in CATEGORIES.items()
        }
        tags = {
            slug: Tag.objects.get_or_create(slug=slug, defaults={"name": name})[0]
            for slug, name in TAGS.items()
        }

        now = timezone.now()
        created = 0
        for age, data in enumerate(POSTS):
            post, was_created = Post.objects.get_or_create(
                slug=slugify(data["title"]),
                defaults={
                    "title": data["title"],
                    "author": author,
                    "category": categories[data["category"]],
                    "excerpt": data.get("excerpt", ""),
                    "body": data["body"],
                    "status": Post.Status.PUBLISHED,
                    # Oldest first in the list, so the welcome post is the oldest.
                    "published_at": now - timedelta(days=len(POSTS) - age),
                },
            )
            if was_created:
                post.tags.set(tags[slug] for slug in data["tags"])
                created += 1

        Page.objects.get_or_create(
            slug="about",
            defaults={"title": "About", "body": ABOUT, "is_published": True, "nav_order": 1},
        )

        self.stdout.write(self.style.SUCCESS(f"Demo content ready ({created} new posts)."))

    def get_author(self, email):
        User = get_user_model()
        if email:
            try:
                return User.objects.get_by_natural_key(email)
            except User.DoesNotExist:
                raise CommandError(f"No user with email {email}.") from None
        author = User.objects.filter(is_superuser=True).order_by("pk").first()
        if author is None:
            raise CommandError("Create a superuser first: python manage.py createsuperuser")
        return author
