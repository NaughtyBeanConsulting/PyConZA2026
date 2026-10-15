from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy

from .models import Post


class LatestPostsFeed(Feed):
    title = settings.SITE_NAME
    link = reverse_lazy("blog:post_list")
    description = f"Latest posts from {settings.SITE_NAME}."

    def items(self):
        return Post.objects.published().select_related("author")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_author_name(self, item):
        return item.author.display_name
