"""Copie le contenu existant des articles dans les colonnes « _fr » (voir portfolio/migrations/0006)."""

from django.db import migrations
from django.db.models import F

POST_FIELDS = ["title", "excerpt", "content", "tags"]


def copy_to_french(apps, schema_editor):
    post = apps.get_model("blog", "Post")
    for field in POST_FIELDS:
        post.objects.filter(**{f"{field}_fr__isnull": True}).update(**{f"{field}_fr": F(field)})


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0002_post_content_en_post_content_fr_post_excerpt_en_and_more"),
    ]

    operations = [
        migrations.RunPython(copy_to_french, migrations.RunPython.noop),
    ]
