"""
Copie le contenu existant (écrit en français) dans les nouvelles colonnes « _fr » (django-modeltranslation).

Sans cette étape, les textes déjà saisis resteraient dans la colonne d'origine et le site afficherait des
champs vides. Opération sûre et rejouable : on ne touche que les lignes dont la colonne « _fr » est encore vide.
"""

from django.db import migrations
from django.db.models import F

TRANSLATED_FIELDS = {
    "Profile": ["headline", "roles", "tagline", "about", "languages", "location"],
    "Service": ["title", "description"],
    "Skill": ["name"],
    "TimelineItem": ["title", "organization", "description"],
    "Project": ["title", "description", "technologies"],
    "Testimonial": ["author_role", "content"],
    "FAQ": ["question", "answer"],
}


def copy_to_french(apps, schema_editor):
    for model_name, fields in TRANSLATED_FIELDS.items():
        model = apps.get_model("portfolio", model_name)
        for field in fields:
            model.objects.filter(**{f"{field}_fr__isnull": True}).update(**{f"{field}_fr": F(field)})


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0005_faq_answer_en_faq_answer_fr_faq_question_en_and_more"),
    ]

    operations = [
        migrations.RunPython(copy_to_french, migrations.RunPython.noop),
    ]
