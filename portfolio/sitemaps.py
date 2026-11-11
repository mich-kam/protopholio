from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post
from courses.models import Course


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["portfolio:home", "portfolio:cv", "portfolio:security", "courses:list", "blog:list"]

    def location(self, item):
        return reverse(item)


class CourseSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Course.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class PostSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {"pages": StaticViewSitemap, "courses": CourseSitemap, "blog": PostSitemap}
