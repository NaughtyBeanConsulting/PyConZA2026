from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Category, Page, Post, Tag

User = get_user_model()
HTMX = {"HTTP_HX_REQUEST": "true"}


def make_post(author, title, status=Post.Status.PUBLISHED, **kwargs):
    return Post.objects.create(
        author=author, title=title, slug=title.lower().replace(" ", "-"),
        body=f"<p>{title} body</p>", status=status, **kwargs,
    )


class PostModelTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user("writer@example.com", "pw")

    def test_publishing_stamps_published_at(self):
        post = make_post(self.author, "Hello")
        self.assertIsNotNone(post.published_at)
        self.assertIsNone(make_post(self.author, "Draft", Post.Status.DRAFT).published_at)

    def test_published_excludes_drafts_and_scheduled(self):
        live = make_post(self.author, "Live")
        make_post(self.author, "Draft", Post.Status.DRAFT)
        make_post(self.author, "Later", published_at=timezone.now() + timedelta(days=1))
        self.assertQuerySetEqual(Post.objects.published(), [live])

    def test_body_is_sanitized_on_save(self):
        post = make_post(self.author, "Xss")
        post.body = '<p onclick="steal()">Hi</p><script>alert(1)</script>'
        post.save()
        self.assertEqual(post.body, "<p>Hi</p>")

    def test_reading_minutes(self):
        post = Post(body="<p>" + "word " * 450 + "</p>")
        self.assertEqual(post.reading_minutes, 3)


@override_settings(BLOG_POSTS_PER_PAGE=2)
class PostListViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user("writer@example.com", "pw")
        now = timezone.now()
        for i, title in enumerate(["Django tips", "Htmx magic", "Alpine basics"]):
            make_post(self.author, title, published_at=now - timedelta(hours=i))
        make_post(self.author, "Secret draft", Post.Status.DRAFT)

    def test_lists_only_published(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertContains(response, "Django tips")
        self.assertNotContains(response, "Secret draft")
        self.assertContains(response, "<html", html=False)

    def test_htmx_request_gets_fragment(self):
        response = self.client.get(reverse("blog:post_list"), {"q": "htmx"}, **HTMX)
        self.assertNotContains(response, "<html", html=False)
        self.assertContains(response, "Htmx magic")
        self.assertNotContains(response, "Django tips")
        self.assertIn("HX-Request", response["Vary"])

    def test_history_restore_gets_full_page(self):
        response = self.client.get(
            reverse("blog:post_list"), HTTP_HX_HISTORY_RESTORE_REQUEST="true", **HTMX
        )
        self.assertContains(response, "<html", html=False)

    def test_load_more(self):
        first = self.client.get(reverse("blog:post_list"))
        self.assertContains(first, "Load more posts")
        self.assertNotContains(first, "Alpine basics")
        more = self.client.get(reverse("blog:post_list"), {"page": 2}, **HTMX)
        self.assertContains(more, "Alpine basics")
        self.assertNotContains(more, "Load more posts")

    def test_empty_search(self):
        response = self.client.get(reverse("blog:post_list"), {"q": "nothing-here"}, **HTMX)
        self.assertContains(response, "No posts match")

    def test_category_and_tag_filters(self):
        python = Category.objects.create(name="Python", slug="python")
        tag = Tag.objects.create(name="web", slug="web")
        post = Post.objects.get(slug="django-tips")
        post.category = python
        post.save()
        post.tags.add(tag)
        for url in (python.get_absolute_url(), tag.get_absolute_url()):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "Django tips")
                self.assertNotContains(response, "Htmx magic")

    def test_feed(self):
        response = self.client.get(reverse("blog:feed"))
        self.assertContains(response, "Django tips")
        self.assertNotContains(response, "Secret draft")


class DetailViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user("writer@example.com", "pw")
        self.staff = User.objects.create_user("editor@example.com", "pw", is_staff=True)
        self.draft = make_post(self.author, "Draft post", Post.Status.DRAFT)

    def test_draft_hidden_from_public(self):
        self.assertEqual(self.client.get(self.draft.get_absolute_url()).status_code, 404)

    def test_staff_can_preview_draft(self):
        self.client.force_login(self.staff)
        response = self.client.get(self.draft.get_absolute_url())
        self.assertContains(response, "Preview.")

    def test_published_post_has_older_newer(self):
        older = make_post(self.author, "Older", published_at=timezone.now() - timedelta(days=2))
        middle = make_post(self.author, "Middle", published_at=timezone.now() - timedelta(days=1))
        response = self.client.get(middle.get_absolute_url())
        self.assertEqual(response.context["older"], older)
        self.assertIsNone(response.context["newer"])

    def test_page(self):
        page = Page.objects.create(title="About", slug="about", body="<p>Us</p>", is_published=True)
        hidden = Page.objects.create(title="Soon", slug="soon", body="<p>x</p>")
        response = self.client.get(page.get_absolute_url())
        self.assertContains(response, "Us")
        self.assertContains(self.client.get("/"), 'href="/about/"')  # in the nav
        self.assertEqual(self.client.get(hidden.get_absolute_url()).status_code, 404)

    def test_page_slug_cannot_shadow_site_urls(self):
        with self.assertRaises(ValidationError):
            Page(title="Admin", slug="admin", body="x").full_clean()
        Page(title="About", slug="about", body="x").full_clean()


class PostAdminTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("boss@example.com", "pw")
        self.client.force_login(self.admin)

    def test_admin_pages_render(self):
        post = make_post(self.admin, "Hello")
        for url in (
            reverse("admin:index"),
            reverse("admin:blog_post_changelist"),
            reverse("admin:blog_post_add"),
            reverse("admin:blog_post_change", args=[post.pk]),
            reverse("admin:blog_page_add"),
            reverse("admin:blog_category_changelist"),
            reverse("admin:blog_tag_changelist"),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_add_form_defaults_author_to_current_user(self):
        response = self.client.get(reverse("admin:blog_post_add"))
        self.assertEqual(response.context["adminform"].form.initial["author"], self.admin.pk)

    def test_publish_action(self):
        draft = make_post(self.admin, "Draft", Post.Status.DRAFT)
        self.client.post(
            reverse("admin:blog_post_changelist"),
            {"action": "publish", "_selected_action": [draft.pk]},
        )
        draft.refresh_from_db()
        self.assertEqual(draft.status, Post.Status.PUBLISHED)
        self.assertIsNotNone(draft.published_at)
