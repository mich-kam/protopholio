"""Chiffres et raccourcis du tableau de bord de l'administration."""

from django.urls import reverse

from blog.models import Post
from courses.models import Course, Order
from portfolio.models import ContactMessage, GalleryPhoto, Project


def unread_messages(request):
    """Pastille sur « Messages » : nombre de messages non lus, masquée s'il n'y en a pas."""
    count = ContactMessage.objects.filter(is_read=False).count()
    return str(count) if count else None


def dashboard_callback(request, context):
    cards = [
        ("Messages non lus", ContactMessage.objects.filter(is_read=False).count(), "admin:portfolio_contactmessage_changelist", "mail"),
        ("Projets publiés", Project.objects.count(), "admin:portfolio_project_changelist", "work"),
        ("Photos", GalleryPhoto.objects.filter(is_published=True).count(), "admin:portfolio_galleryphoto_changelist", "photo_library"),
        ("Cours en ligne", Course.objects.filter(is_published=True).count(), "admin:courses_course_changelist", "school"),
        ("Commandes payées", Order.objects.filter(status=Order.Status.PAID).count(), "admin:courses_order_changelist", "shopping_bag"),
        ("Articles", Post.objects.filter(is_published=True).count(), "admin:blog_post_changelist", "article"),
    ]
    actions = [
        ("Ajouter un projet", "admin:portfolio_project_add"),
        ("Ajouter une photo", "admin:portfolio_galleryphoto_add"),
        ("Ajouter un cours", "admin:courses_course_add"),
        ("Ajouter un article", "admin:blog_post_add"),
    ]
    context["dashboard_cards"] = [
        {"label": label, "value": value, "link": reverse(url), "icon": icon}
        for label, value, url, icon in cards
    ]
    context["dashboard_actions"] = [
        {"label": label, "link": reverse(url)} for label, url in actions
    ]
    context["site_home"] = "/"
    return context
