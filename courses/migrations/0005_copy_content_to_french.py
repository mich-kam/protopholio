"""Copie le contenu existant des cours dans les colonnes « _fr » (voir portfolio/migrations/0006)."""

from django.db import migrations
from django.db.models import F

COURSE_FIELDS = ["title", "short_description", "description", "duration", "learning_outcomes", "requirements"]


def copy_to_french(apps, schema_editor):
    course = apps.get_model("courses", "Course")
    for field in COURSE_FIELDS:
        course.objects.filter(**{f"{field}_fr__isnull": True}).update(**{f"{field}_fr": F(field)})


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0004_course_description_en_course_description_fr_and_more"),
    ]

    operations = [
        migrations.RunPython(copy_to_french, migrations.RunPython.noop),
    ]
