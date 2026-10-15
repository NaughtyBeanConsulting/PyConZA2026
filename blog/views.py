from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils.cache import patch_vary_headers

from .models import Category, Page, Post, Tag


def wants_fragment(request):
    """True for htmx swaps; False for normal loads and htmx history restores."""
    return (
        request.headers.get("HX-Request") == "true"
        and request.headers.get("HX-History-Restore-Request") != "true"
    )


def post_list(request, category_slug=None, tag_slug=None):
    posts = Post.objects.published().select_related("author", "category")
    category = tag = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=tag)

    query = request.GET.get("q", "").strip()
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(body__icontains=query)
        )

    page_obj = Paginator(posts, settings.BLOG_POSTS_PER_PAGE).get_page(request.GET.get("page"))
    context = {"page_obj": page_obj, "query": query, "category": category, "tag": tag}

    # htmx search and "load more" only need the cards, not the whole page.
    template = "blog/post_list.html"
    if wants_fragment(request):
        template += "#post-cards"
    response = render(request, template, context)
    patch_vary_headers(response, ["HX-Request"])
    return response


def post_detail(request, slug):
    posts = Post.objects.select_related("author", "category").prefetch_related("tags")
    if not request.user.is_staff:
        posts = posts.published()  # staff can preview drafts and scheduled posts
    post = get_object_or_404(posts, slug=slug)

    newer = older = None
    if post.is_live:
        live = Post.objects.published()
        older = live.filter(published_at__lt=post.published_at).first()
        newer = live.filter(published_at__gt=post.published_at).order_by("published_at").first()

    return render(request, "blog/post_detail.html", {"post": post, "newer": newer, "older": older})


def page_detail(request, slug):
    pages = Page.objects.all() if request.user.is_staff else Page.objects.filter(is_published=True)
    page = get_object_or_404(pages, slug=slug)
    return render(request, "blog/page_detail.html", {"page": page})
