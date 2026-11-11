from django.urls import path

from . import views
from .feeds import LatestPostsFeed

app_name = "blog"

urlpatterns = [
    path("blog/", views.post_list, name="list"),
    path("blog/rss.xml", LatestPostsFeed(), name="rss"),
    path("blog/<slug:slug>/", views.post_detail, name="detail"),
]
