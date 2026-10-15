from django.urls import path

from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("feed/", LatestPostsFeed(), name="feed"),
    path("posts/<slug:slug>/", views.post_detail, name="post_detail"),
    path("category/<slug:category_slug>/", views.post_list, name="category"),
    path("tag/<slug:tag_slug>/", views.post_list, name="tag"),
    # Catch-all for CMS pages — keep last.
    path("<slug:slug>/", views.page_detail, name="page"),
]
