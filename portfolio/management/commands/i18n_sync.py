"""
Gestion des traductions SANS GNU gettext (compatible Windows) : extraction, mise à jour du .po, compilation du .mo.

    python manage.py i18n_sync              # extrait les textes, met à jour locale/en/.../django.po et compile le .mo
    python manage.py i18n_sync --list       # affiche (et écrit dans locale/untranslated.txt) les textes sans traduction
    python manage.py i18n_sync --import F   # importe des traductions depuis un fichier « N|traduction » (voir --list)
    python manage.py i18n_sync --check      # code de sortie 1 s'il manque une traduction (pour l'intégration continue)

Les textes sources sont en français (langue du site) : chaque texte français est un « msgid » et sa traduction
anglaise le « msgstr ». Les fichiers .mo compilés sont versionnés : le déploiement n'a donc pas besoin de gettext.

Nécessite Babel (outil de développement, voir requirements-dev.txt). Si GNU gettext est installé, la commande
standard `makemessages` / `compilemessages` de Django reste utilisable à la place.
"""

import io
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation.template import templatize

SOURCE_LANGUAGE = "fr"
TARGET_LANGUAGES = ["en"]

PY_KEYWORDS = {
    "gettext": None,
    "gettext_lazy": None,
    "ngettext": (1, 2),
    "ngettext_lazy": (1, 2),
    "pgettext": ((1, "c"), 2),
    "pgettext_lazy": ((1, "c"), 2),
    "_": None,
}
PLACEHOLDER = re.compile(r"%\((\w+)\)[sdif]")
EXCLUDED_PARTS = {".venv", "venv", "migrations", "staticfiles", "node_modules", "__pycache__", "locale", "tools"}


def _project_files():
    root = Path(settings.BASE_DIR)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or EXCLUDED_PARTS & set(path.relative_to(root).parts):
            continue
        name = path.name
        if path.suffix in {".html", ".txt"} and "templates" in path.relative_to(root).parts:
            yield path, "template"
        elif path.suffix == ".py" and not name.startswith("test") and name != "tests.py":
            yield path, "python"


def extract_messages():
    """Retourne {(contexte, msgid, msgid_pluriel_ou_None): [(fichier, ligne), ...]}."""
    try:
        from babel.messages.extract import extract
    except ImportError as exc:  # pragma: no cover
        raise CommandError("Babel est requis : pip install Babel (voir requirements-dev.txt).") from exc

    root = Path(settings.BASE_DIR)
    found = {}
    for path, kind in _project_files():
        relative = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8")
        if kind == "template":
            source = templatize(source, origin=str(path))  # même pré-traitement que `makemessages`
            # xgettext tolère l'indentation arbitraire produite par templatize, pas le tokenizer de Python.
            source = "\n".join(line.lstrip() for line in source.splitlines())
        stream = io.BytesIO(source.encode("utf-8"))
        for lineno, message, _comments, context in extract("python", stream, keywords=PY_KEYWORDS, options={}):
            singular, plural = (message[0], message[1]) if isinstance(message, tuple) else (message, None)
            if not singular:
                continue
            found.setdefault((context, singular, plural), []).append((relative, lineno))
    return found


def _po_path(language):
    return Path(settings.LOCALE_PATHS[0]) / language / "LC_MESSAGES" / "django.po"


def _load_catalog(language):
    from babel.messages.pofile import read_po

    path = _po_path(language)
    if path.exists():
        with path.open("rb") as handle:
            return read_po(handle, locale=language, domain="django")
    return None


def _placeholders(text):
    return sorted(PLACEHOLDER.findall(text or ""))


def build_catalog(language, found):
    """Fusionne les textes extraits avec les traductions existantes (rien n'est perdu ni écrasé)."""
    from babel.messages.catalog import Catalog

    old = _load_catalog(language)
    catalog = Catalog(
        locale=language,
        domain="django",
        project="Portfolio",
        charset="utf-8",
        header_comment=f"# Traductions {language} — textes sources en français.\n# Généré par `manage.py i18n_sync`.",
    )
    for (context, singular, plural), locations in sorted(found.items(), key=lambda kv: (kv[0][1], kv[0][0] or "")):
        previous = old.get(singular, context=context) if old else None
        if plural:
            msgid = (singular, plural)
            kept = previous.string if previous and isinstance(previous.string, (tuple, list)) else ()
            string = tuple(kept) if len(kept) == 2 else ("", "")
        else:
            msgid = singular
            string = previous.string if previous and isinstance(previous.string, str) else ""
        catalog.add(msgid, string=string, locations=sorted(set(locations)), context=context)
    return catalog


def untranslated(catalog):
    result = []
    for message in catalog:
        if not message.id:
            continue
        strings = message.string if isinstance(message.string, (tuple, list)) else [message.string]
        if not all(strings):
            result.append(message)
    return sorted(result, key=lambda m: m.id if isinstance(m.id, str) else m.id[0])


def write_files(language, catalog):
    from babel.messages.mofile import write_mo
    from babel.messages.pofile import write_po

    po = _po_path(language)
    po.parent.mkdir(parents=True, exist_ok=True)
    with po.open("wb") as handle:
        write_po(handle, catalog, width=100, sort_output=True, include_lineno=True)
    with po.with_suffix(".mo").open("wb") as handle:
        write_mo(handle, catalog)


class Command(BaseCommand):
    help = "Extrait, met à jour et compile les traductions (sans GNU gettext)."

    def add_arguments(self, parser):
        parser.add_argument("--list", action="store_true", help="Liste les textes non traduits.")
        parser.add_argument("--check", action="store_true", help="Échoue s'il manque une traduction.")
        parser.add_argument("--import", dest="import_file", help="Fichier « N|traduction » à importer.")

    def handle(self, *args, **options):
        found = extract_messages()
        self.stdout.write(f"{len(found)} textes traduisibles trouvés dans le projet.")
        exit_code = 0

        for language in TARGET_LANGUAGES:
            catalog = build_catalog(language, found)

            if options["import_file"]:
                self._import(catalog, Path(options["import_file"]))

            missing = untranslated(catalog)
            write_files(language, catalog)
            self.stdout.write(self.style.SUCCESS(f"[{language}] .po et .mo écrits — {len(missing)} texte(s) sans traduction."))

            if options["list"]:
                lines = []
                for number, message in enumerate(missing, start=1):
                    msgid = message.id if isinstance(message.id, str) else " ||| ".join(message.id)
                    lines.append(f"{number}|{msgid}")
                target = Path(settings.LOCALE_PATHS[0]) / "untranslated.txt"
                target.write_text("\n".join(lines), encoding="utf-8")
                self.stdout.write(f"Liste écrite dans {target}")
            if options["check"] and missing:
                exit_code = 1
                for message in missing[:20]:
                    self.stdout.write(self.style.WARNING(f"  manquant : {message.id!r}"))

        if exit_code:
            raise CommandError("Des traductions sont manquantes.")

    def _import(self, catalog, path):
        missing = untranslated(catalog)
        by_number = {number: message for number, message in enumerate(missing, start=1)}
        applied = problems = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            if not raw.strip() or raw.startswith("#"):
                continue
            number_text, _sep, translation = raw.partition("|")
            message = by_number.get(int(number_text))
            if message is None:
                self.stdout.write(self.style.WARNING(f"  numéro inconnu : {number_text}"))
                problems += 1
                continue
            if isinstance(message.id, tuple):  # pluriel : « singulier ||| pluriel »
                forms = [part.strip() for part in translation.split("|||")]
                if len(forms) != 2:
                    self.stdout.write(self.style.WARNING(f"  {number_text}: 2 formes attendues (singulier ||| pluriel)"))
                    problems += 1
                    continue
                expected = _placeholders(message.id[1])
                if any(_placeholders(form) != expected for form in forms):
                    self.stdout.write(self.style.WARNING(f"  {number_text}: variables différentes : {forms}"))
                    problems += 1
                    continue
                message.string = tuple(forms)
            else:
                translation = translation.strip()
                if _placeholders(translation) != _placeholders(message.id):
                    self.stdout.write(self.style.WARNING(f"  {number_text}: variables différentes : {translation!r}"))
                    problems += 1
                    continue
                message.string = translation
            applied += 1
        self.stdout.write(f"{applied} traductions importées, {problems} problème(s).")
