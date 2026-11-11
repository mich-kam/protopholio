from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.translation import gettext as _

from portfolio.models import Profile

from .models import Post

FEED_ITEMS = 20


class LatestPostsFeed(Feed):
    """Flux RSS du blog : /blog/rss.xml (lecteurs RSS, agrégateurs, newsletters automatiques)."""

    def description(self):
        return _("Articles sur la cybersécurité, le développement web et les réseaux.")

    def title(self):
        profile = Profile.objects.first()
        return _("Blog — %(name)s") % {"name": profile.full_name} if profile else _("Blog")

    def link(self):
        return reverse("blog:list")

    def items(self):
        return Post.objects.published()[:FEED_ITEMS]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_categories(self, item):
        return item.tag_list
