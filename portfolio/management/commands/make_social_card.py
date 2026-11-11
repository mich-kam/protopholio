"""
Génère l'image d'aperçu affichée quand le site est partagé (WhatsApp, Facebook, LinkedIn...).

    python manage.py make_social_card

Le résultat est écrit dans static/img/social-card.jpg (1200x630, format recommandé par Open Graph).
À relancer après un changement de nom, de titre, de rôles ou de photo.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageFont, ImageOps

from portfolio.models import DEFAULT_PHOTO, Profile

WIDTH, HEIGHT = 1200, 630
OUTPUT = Path(settings.BASE_DIR) / "static" / "img" / "social-card.jpg"

# Dégradé de la marque : indigo -> violet -> fuchsia
GRADIENT = ((79, 70, 229), (124, 58, 237), (192, 38, 211))


# Polices recherchées dans l'ordre (Windows, macOS, Linux) : il en faut une qui gère les accents.
FONT_CANDIDATES = {
    True: [  # gras
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ],
    False: [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ],
}


def _font(size, bold=False):
    for path in FONT_CANDIDATES[bold]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    # Dernier recours : police intégrée à Pillow (les caractères accentués peuvent mal s'afficher).
    return ImageFont.load_default(size=size)


def _gradient():
    base = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = base.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            t = (x / WIDTH * 0.6) + (y / HEIGHT * 0.4)  # diagonale
            seg, local = (0, t * 2) if t < 0.5 else (1, (t - 0.5) * 2)
            a, b = GRADIENT[seg], GRADIENT[seg + 1]
            pixels[x, y] = tuple(int(a[i] + (b[i] - a[i]) * local) for i in range(3))
    return base


def _wrap(draw, text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


class Command(BaseCommand):
    help = "Génère static/img/social-card.jpg à partir du profil."

    def handle(self, *args, **options):
        profile = Profile.objects.first()
        if not profile:
            raise CommandError("Aucun profil : créez-le dans l'admin (ou lancez seed_demo) puis relancez.")

        card = _gradient()
        draw = ImageDraw.Draw(card, "RGBA")

        # Motif de points discret
        for gx in range(0, WIDTH, 28):
            for gy in range(0, HEIGHT, 28):
                draw.ellipse((gx, gy, gx + 2, gy + 2), fill=(255, 255, 255, 40))

        # Photo en médaillon circulaire
        photo_path = Path(profile.photo.path) if profile.photo else Path(settings.BASE_DIR) / "static" / DEFAULT_PHOTO
        text_left = 80
        if photo_path.exists():
            size = 400
            photo = ImageOps.fit(Image.open(photo_path).convert("RGB"), (size, size), centering=(0.5, 0.18))
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
            cx, cy = 80 + size // 2, HEIGHT // 2
            draw.ellipse((cx - size // 2 - 10, cy - size // 2 - 10, cx + size // 2 + 10, cy + size // 2 + 10), fill=(255, 255, 255, 235))
            card.paste(photo, (cx - size // 2, cy - size // 2), mask)
            text_left = 80 + size + 70

        max_width = WIDTH - text_left - 70
        y = 150
        name_font = _font(68, bold=True)
        for line in _wrap(draw, profile.full_name, name_font, max_width):
            draw.text((text_left, y), line, font=name_font, fill="white")
            y += 80
        y += 12
        headline_font = _font(34)
        for line in _wrap(draw, profile.headline, headline_font, max_width):
            draw.text((text_left, y), line, font=headline_font, fill=(238, 232, 255))
            y += 44

        # Pastilles de rôles
        chip_font = _font(24, bold=True)
        x, y = text_left, y + 26
        for role in profile.roles_list[:3]:
            w = int(draw.textlength(role, font=chip_font)) + 36
            if x + w > WIDTH - 60:
                x, y = text_left, y + 56
            draw.rounded_rectangle((x, y, x + w, y + 44), radius=22, fill=(255, 255, 255, 38), outline=(255, 255, 255, 120))
            draw.text((x + 18, y + 8), role, font=chip_font, fill="white")
            x += w + 14

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        card.save(OUTPUT, "JPEG", quality=90, optimize=True, progressive=True)
        self.stdout.write(self.style.SUCCESS(f"Image générée : {OUTPUT} ({OUTPUT.stat().st_size // 1024} Ko)"))
