from collections import Counter

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import translation

from portfolio.context_processors import get_profile
from portfolio.seo import jsonld

from .models import Post

POSTS_PER_PAGE = 6
RELATED_POSTS = 3


def _tag_counts():
    """[(tag, nombre d'articles), ...] trié du plus utilisé au moins utilisé."""
    counter = Counter()
    for tags in Post.objects.published().values_list("tags", flat=True):
        for tag in (t.strip() for t in tags.split(",")):
            if tag:
                counter[tag] += 1
    return counter.most_common()


def post_list(request):
    """Liste des articles : recherche, filtre par tag, pagination."""
    q = request.GET.get("q", "").strip()[:100]
    tag = request.GET.get("tag", "").strip()[:50]

    posts = Post.objects.published()
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q))
    if tag:
        wanted = tag.lower()
        # Filtre en Python : les tags sont stockés dans un champ texte et la liste reste petite.
        ids = [p.pk for p in posts.only("id", "tags") if wanted in (t.lower() for t in p.tag_list)]
        posts = posts.filter(pk__in=ids)

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # L'article « à la une » n'est mis en avant que sur la première page, sans recherche ni filtre.
    featured = None
    if page_obj.number == 1 and not (q or tag):
        featured = posts.filter(is_featured=True).first()

    return render(
        request,
        "blog/post_list.html",
        {
            "posts": [p for p in page_obj if not featured or p.pk != featured.pk],
            "page_obj": page_obj,
            "featured": featured,
            "total": paginator.count,
            "q": q,
            "tag": tag,
            "tags": _tag_counts(),
        },
    )


def _related(post):
    """Articles proches : ceux qui partagent le plus de tags, puis les plus récents."""
    mine = {t.lower() for t in post.tag_list}
    others = list(Post.objects.published().exclude(pk=post.pk))
    others.sort(key=lambda p: (-len(mine & {t.lower() for t in p.tag_list}), -p.published_at.timestamp()))
    return others[:RELATED_POSTS]


def _article_jsonld(request, post):
    profile = get_profile(request)
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.excerpt,
        "datePublished": post.published_at.isoformat(),
        "dateModified": post.updated_at.isoformat(),
        "mainEntityOfPage": request.build_absolute_uri(post.get_absolute_url()),
        "inLanguage": translation.get_language(),
    }
    if post.cover:
        data["image"] = request.build_absolute_uri(post.cover.url)
    if profile:
        data["author"] = {"@type": "Person", "name": profile.full_name}
    return jsonld(data)


def post_detail(request, slug):
    # Le personnel peut prévisualiser un brouillon ou un article programmé ; le public ne voit que le publié.
    queryset = Post.objects.all() if request.user.is_staff else Post.objects.published()
    post = get_object_or_404(queryset, slug=slug)
    published = Post.objects.published()
    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "related_posts": _related(post),
            "previous_post": published.filter(published_at__lt=post.published_at).order_by("-published_at").first(),
            "next_post": published.filter(published_at__gt=post.published_at).order_by("published_at").first(),
            "jsonld": _article_jsonld(request, post),
        },
    )
