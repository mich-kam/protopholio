"""
Outil ponctuel (développement) : enveloppe les textes français « simples » des gabarits HTML dans
{% trans "..." %} pour les rendre traduisibles.

    python tools/wrap_templates.py            # essai à blanc : affiche ce qui serait modifié
    python tools/wrap_templates.py --apply    # applique les modifications

Règles :
- seuls les nœuds de texte purement littéraux sont enveloppés ;
- un texte collé à une variable {{ ... }} (phrase composée) est SIGNALÉ, jamais modifié : il se traduit à la main
  avec {% blocktrans %} ;
- <script>, <style>, <pre>, <textarea>, <svg> et les commentaires sont ignorés ;
- les attributs aria-label / title / alt / placeholder purement littéraux sont enveloppés aussi.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

TOKEN = re.compile(r"(\{#.*?#\}|\{%.*?%\}|\{\{.*?\}\}|<!--.*?-->|<[^>]*>)", re.S)
SKIP_TAGS = {"script", "style", "pre", "textarea", "svg"}
ATTRS = ("aria-label", "title", "alt", "placeholder")
ATTR_RE = re.compile(r'(\s(?:' + "|".join(ATTRS) + r')=)"([^"]*)"')
ENTITY = re.compile(r"&#?\w+;")
LETTER = re.compile(r"[A-Za-zÀ-ÿ]")
TAG_NAME = re.compile(r"^<(/?)\s*([a-zA-Z][\w-]*)")


def has_words(text):
    """Vrai si le texte contient de vraies lettres (hors entités HTML) et plus de 2 caractères."""
    plain = ENTITY.sub("", text).strip()
    return bool(LETTER.search(plain)) and len(plain) > 2


def quote(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def line_of(src, index):
    return src.count("\n", 0, index) + 1


def process(src, name, report):
    parts = TOKEN.split(src)  # [texte, jeton, texte, jeton, ...]
    out, pos, skipping = [], 0, None
    for i, part in enumerate(parts):
        start = pos
        pos += len(part)
        is_token = i % 2 == 1

        if is_token:
            match = TAG_NAME.match(part)
            opened_now = False
            if match and not part.startswith("<!--"):
                closing, tag = match.group(1) == "/", match.group(2).lower()
                if skipping and closing and tag == skipping:
                    skipping = None
                elif not skipping and not closing and tag in SKIP_TAGS and not part.rstrip().endswith("/>"):
                    skipping = tag
                    opened_now = True

            # Attributs littéraux d'une balise ouvrante (y compris celle qui ouvre un bloc ignoré, ex. <svg aria-label=...>)
            if match and not part.startswith("<!--") and match.group(1) != "/" and (not skipping or opened_now):
                def repl(m):
                    value = m.group(2)
                    if "{%" in value or "{{" in value:
                        report["manual"].append(f"{name}:{line_of(src, start)}  attribut avec variable : {m.group(0).strip()[:90]}")
                        return m.group(0)
                    if not has_words(value):
                        return m.group(0)
                    report["attrs"] += 1
                    return f'{m.group(1)}"{{% trans {quote(value)} %}}"'

                part = ATTR_RE.sub(repl, part)
            out.append(part)
            continue

        # --- nœud de texte ---
        if skipping or not has_words(part):
            out.append(part)
            continue
        prev_tok = parts[i - 1] if i > 0 else ""
        next_tok = parts[i + 1] if i + 1 < len(parts) else ""
        if prev_tok.startswith("{{") or next_tok.startswith("{{"):
            report["manual"].append(f"{name}:{line_of(src, start)}  texte collé à une variable : {' '.join(part.split())[:90]!r}")
            out.append(part)
            continue
        lead = part[: len(part) - len(part.lstrip())]
        trail = part[len(part.rstrip()):]
        text = " ".join(part.split())
        report["texts"] += 1
        out.append(f"{lead}{{% trans {quote(text)} %}}{trail}")
    return "".join(out)


def main():
    apply = "--apply" in sys.argv
    total = {"texts": 0, "attrs": 0, "manual": []}
    for path in sorted(TEMPLATES.rglob("*.html")):
        src = path.read_text(encoding="utf-8")
        report = {"texts": 0, "attrs": 0, "manual": []}
        new = process(src, path.relative_to(ROOT).as_posix(), report)
        total["texts"] += report["texts"]
        total["attrs"] += report["attrs"]
        total["manual"] += report["manual"]
        print(f"{path.relative_to(TEMPLATES).as_posix():<42} textes : {report['texts']:>3}  attributs : {report['attrs']:>2}  à la main : {len(report['manual']):>2}")
        if apply and new != src:
            path.write_text(new, encoding="utf-8", newline="\n")
    print(f"\nTOTAL : {total['texts']} textes, {total['attrs']} attributs, {len(total['manual'])} cas manuels")
    if "--list" in sys.argv:
        print("\n".join(total["manual"]))
    print("(essai à blanc : rien n'a été écrit)" if not apply else "Modifications écrites.")


if __name__ == "__main__":
    main()
