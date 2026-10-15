from django.contrib import admin, messages
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action, display

from .models import Category, Page, Post, Tag

RICH_TEXT_FIELDS = {"body"}


class RichTextAdminMixin:
    """Edit the `body` field with Unfold's WYSIWYG (Trix) editor."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in RICH_TEXT_FIELDS:
            kwargs["widget"] = WysiwygWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class PostCountMixin:
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_post_count=Count("posts"))

    @display(description=_("Posts"), ordering="_post_count")
    def post_count(self, obj):
        return obj._post_count


@admin.register(Category)
class CategoryAdmin(PostCountMixin, ModelAdmin):
    list_display = ["name", "slug", "post_count"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(PostCountMixin, ModelAdmin):
    list_display = ["name", "slug", "post_count"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(RichTextAdminMixin, ModelAdmin):
    list_display = ["title", "status_badge", "category", "author", "published_at", "updated_at"]
    list_filter = ["status", "category", "tags", "author"]
    search_fields = ["title", "excerpt", "body"]
    date_hierarchy = "published_at"
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["category", "tags"]
    list_select_related = ["category", "author"]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["publish", "unpublish"]
    fieldsets = (
        (None, {"fields": ("title", "slug", "body")}),
        (_("Summary"), {"fields": ("excerpt",)}),
        (_("Publishing"), {"fields": ("status", "published_at", "author")}),
        (_("Organisation"), {"fields": ("category", "tags")}),
        (_("History"), {"fields": ("created_at", "updated_at"), "classes": ["collapse"]}),
    )

    def get_changeform_initial_data(self, request):
        return {"author": request.user.pk, **super().get_changeform_initial_data(request)}

    @display(
        description=_("Status"),
        ordering="status",
        label={Post.Status.DRAFT: "warning", Post.Status.PUBLISHED: "success"},
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @action(description=_("Publish selected posts"))
    def publish(self, request, queryset):
        queryset.filter(published_at__isnull=True).update(published_at=timezone.now())
        count = queryset.update(status=Post.Status.PUBLISHED)
        self.message_user(
            request,
            ngettext("%d post published.", "%d posts published.", count) % count,
            messages.SUCCESS,
        )

    @action(description=_("Move selected posts back to draft"))
    def unpublish(self, request, queryset):
        count = queryset.update(status=Post.Status.DRAFT)
        self.message_user(
            request,
            ngettext("%d post moved to draft.", "%d posts moved to draft.", count) % count,
            messages.SUCCESS,
        )


@admin.register(Page)
class PageAdmin(RichTextAdminMixin, ModelAdmin):
    list_display = ["title", "slug", "is_published", "show_in_nav", "nav_order", "updated_at"]
    list_editable = ["nav_order"]
    list_filter = ["is_published", "show_in_nav"]
    search_fields = ["title", "body"]
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "body")}),
        (_("Publishing"), {"fields": ("is_published", "show_in_nav", "nav_order")}),
    )
