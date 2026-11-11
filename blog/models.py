import math

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

WORDS_PER_MINUTE = 200


class PostQuerySet(models.QuerySet):
    def published(self):
        """Articles visibles : publiés ET dont la date de publication est atteinte (publication programmable)."""
        return self.filter(is_published=True, published_at__lte=timezone.now())


class Post(models.Model):
    title = models.CharField("titre", max_length=180)
    slug = models.SlugField("slug (URL)", max_length=200, unique=True, blank=True)
    excerpt = models.CharField("résumé", max_length=300, help_text="Affiché dans les listes et lors des partages.")
    content = models.TextField(
        "contenu (Markdown)",
        help_text="Syntaxe Markdown : ## Titre, **gras**, *italique*, - liste, [lien](https://...), > citation, `code`.",
    )
    cover = models.ImageField("image de couverture", upload_to="blog/", blank=True)
    tags = models.CharField("tags", max_length=200, blank=True, help_text="Séparés par des virgules. Ex. : Cybersécurité, Django")
    is_published = models.BooleanField("publié", default=True)
    is_featured = models.BooleanField("à la une", default=False)
    published_at = models.DateTimeField(
        "date de publication", default=timezone.now, help_text="Une date future programme la publication."
    )
    updated_at = models.DateTimeField("modifié le", auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "article"
        verbose_name_plural = "articles"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "article"
            slug, n = base, 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def reading_time(self):
        """Temps de lecture estimé, en minutes (au minimum 1)."""
        return max(1, math.ceil(len(self.content.split()) / WORDS_PER_MINUTE))

    @property
    def is_live(self):
        return self.is_published and self.published_at <= timezone.now()
