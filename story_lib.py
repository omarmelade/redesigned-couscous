"""Lecture des passages (scripts/*.md), partagée par build.py, index.py et avancement.py.

Tolère les fichiers modifiés à la main ou dans le navigateur : en-tête réécrit
en YAML (listes sur plusieurs lignes, guillemets enlevés), fins de ligne Windows,
et passages créés sans en-tête ni sections.
"""
import json, re
from pathlib import Path

root = Path(__file__).parent
FIELDS = ("passage", "tags", "position", "size")
LINK = re.compile(r"\[\[(.*?)\]\]")


def target(link):
    """Nom du passage visé par un lien Twine [[...]]."""
    if "->" in link:
        return link.split("->")[-1]
    if "<-" in link:
        return link.split("<-")[0]
    return link.split("|")[-1]


def _value(raw):
    raw = raw.strip()
    if not raw:
        return ""
    try:
        return json.loads(raw)
    except ValueError:
        if len(raw) > 1 and raw[0] == raw[-1] and raw[0] in "'\"":
            return raw[1:-1]
        return raw


def parse_frontmatter(fm):
    meta, key = {}, None
    for line in fm.split("\n"):
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and key:
            if not isinstance(meta.get(key), list):
                meta[key] = []
            meta[key].append(_value(line.lstrip()[2:]))
        elif ":" in line and not line[0].isspace():
            key, raw = line.split(":", 1)
            key = key.strip()
            meta[key] = _value(raw)
    tags = meta.get("tags")
    if tags in ("", None):
        meta["tags"] = []
    elif isinstance(tags, str):
        meta["tags"] = tags.replace(",", " ").split()
    for k in ("position", "size"):
        meta[k] = "" if meta.get(k) is None else str(meta.get(k))
    return meta


def split(text):
    """Renvoie (en-tête brut ou None, corps)."""
    text = text.replace("\r\n", "\n").lstrip("﻿")
    if text.startswith("---\n"):
        end = text.find("\n---", 3)
        if end != -1:
            nl = text.find("\n", end + 1)
            return text[4:end], ("" if nl == -1 else text[nl + 1:])
    return None, text


def sections(body):
    out, cur = {}, None
    for line in body.split("\n"):
        if line.startswith("## "):
            cur = line[3:].strip(); out[cur] = []
        elif cur:
            out[cur].append(line)
    if not out:  # passage écrit sans sections : tout compte comme Texte
        out["Texte"] = [l for l in body.split("\n") if not l.startswith("# ")]
    return out


class Passage:
    def __init__(self, path):
        self.path = Path(path)
        self.file = self.path.name
        fm, body = split(self.path.read_text(encoding="utf-8"))
        self.has_header = fm is not None
        self.meta = parse_frontmatter(fm or "")
        if not self.meta.get("passage"):
            self.meta["passage"] = self.path.stem
        self.name = self.meta["passage"]
        self.tags = self.meta["tags"]
        self.sections = sections(body)

    def texte(self):
        return "\n".join(self.sections.get("Texte", [])).strip("\n")

    def liens(self):
        """Lignes de la section Liens, sans les lignes de navigation →."""
        return [l for l in self.sections.get("Liens", []) if not l.lstrip().startswith("→")]

    def links(self):
        """[(passage visé, condition)] dans l'ordre de la section Liens."""
        out = []
        for line in self.liens():
            if LINK.search(line):
                cond = " ".join(LINK.sub(" ", line).split())
                out += [(target(t), cond) for t in LINK.findall(line)]
        return out


def load_all():
    return [Passage(f) for f in sorted((root / "scripts").glob("*.md"))]


def link_path(file):
    """Chemin cliquable sur GitHub (les espaces doivent être encodés)."""
    return file.replace(" ", "%20")


def normalize(p, by_name):
    """Met un en-tête et les trois sections si absents, et recalcule les lignes →
    sous chaque lien. Ne touche jamais au Texte ni aux Notes. Renvoie True si modifié."""
    original = p.path.read_text(encoding="utf-8").replace("\r\n", "\n")
    fm, body = split(original)
    if fm is None:
        header = "---\n" + "\n".join(
            f"{k}: {json.dumps(p.meta.get(k, '' if k != 'tags' else []), ensure_ascii=False)}" for k in FIELDS
        ) + "\n---\n"
    else:
        header = original[: len(original) - len(body)]
    lines = body.split("\n")
    if not any(l.startswith("## ") for l in lines):
        texte = "\n".join(l for l in lines if not l.startswith("# ")).strip("\n")
        lines = f"# {p.name.strip()}\n\n## Texte\n\n{texte}\n\n## Notes\n\n\n## Liens\n".split("\n")
    out, cur = [], None
    for line in lines:
        if line.startswith("## "):
            cur = line[3:].strip()
        if cur == "Liens" and line.lstrip().startswith("→"):
            continue
        out.append(line)
        if cur == "Liens" and LINK.search(line):
            for t in LINK.findall(line):
                q = by_name.get(target(t))
                if q:
                    out.append(f"  → [scripts/{q.file}]({link_path(q.file)})")
    new = header + "\n".join(out)
    if new != original:
        p.path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False
