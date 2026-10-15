import math

import nh3
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import Resolver404, resolve, reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

WORDS_PER_MINUTE = 200


def clean_html(html):
    """Strip scripts, event handlers and unknown tags from editor HTML before storing it."""
    return nh3.clean(html)


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category", args=[self.slug])


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:tag", args=[self.slug])


class PostQuerySet(models.QuerySet):
    def published(self):
        """Posts readers can see: published, and not scheduled for the future."""
        return self.filter(status=Post.Status.PUBLISHED, published_at__lte=timezone.now())


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="posts"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        help_text=_("Shown on the post list. Leave blank to use the start of the post."),
    )
    body = models.TextField()
    status = models.CharField(max_length=10, choices=Status, default=Status.DRAFT)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Filled in when first published. Set a future date to schedule the post."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [models.Index(fields=["status", "-published_at"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.body = clean_html(self.body)
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.slug])

    @property
    def is_live(self):
        return (
            self.status == self.Status.PUBLISHED
            and self.published_at is not None
            and self.published_at <= timezone.now()
        )

    @property
    def summary(self):
        return self.excerpt or Truncator(strip_tags(self.body)).words(40)

    @property
    def reading_minutes(self):
        return max(1, math.ceil(len(strip_tags(self.body).split()) / WORDS_PER_MINUTE))


class Page(models.Model):
    """A standalone CMS page (About, Code of Conduct…) served at /<slug>/."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    body = models.TextField()
    is_published = models.BooleanField(default=False)
    show_in_nav = models.BooleanField(
        default=True, help_text=_("List this page in the site's top navigation.")
    )
    nav_order = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nav_order", "title"]

    def __str__(self):
        return self.title

    def clean(self):
        # Pages live at the site root, so a slug that another URL already owns
        # (e.g. "admin") would never be reachable.
        try:
            match = resolve(f"/{self.slug}/")
        except Resolver404:
            return
        if match.view_name != "blog:page":
            raise ValidationError({"slug": _("This address is already used by the site.")})

    def save(self, *args, **kwargs):
        self.body = clean_html(self.body)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:page", args=[self.slug])
