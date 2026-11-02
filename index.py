#!/usr/bin/env python3
"""Reconstruit _index.md dans l'ordre de l'histoire, à partir des sections Liens de scripts/*.md.

Usage : python3 index.py
Les cases déjà cochées dans _index.md sont conservées. Ne lit jamais la section Texte.
Complète aussi les passages sans en-tête ni sections, et remet à jour les lignes →
sous les liens (elles servent seulement à naviguer).
"""
import json, re, sys
from story_lib import root, load_all, normalize, link_path

sys.setrecursionlimit(10000)

passages = load_all()
by_name = {p.name: p for p in passages}
fixed = [p.file for p in passages if normalize(p, by_name)]
if fixed:
    passages = load_all()
    by_name = {p.name: p for p in passages}

story = (root / "_story.twee").read_text(encoding="utf-8")
start = json.loads(story.split(":: StoryData", 1)[1])["start"]

links = {p.name: p.links() for p in passages}
parents = {}
for src, outs in links.items():
    for t, _ in outs:
        parents.setdefault(t, set()).add(src)

checked = set()
idx = root / "_index.md"
if idx.exists():
    text = idx.read_text(encoding="utf-8")
    checked = {f.replace("%20", " ") for f in re.findall(r"- \[[xX]\] (?:\[[^\]]*\]\()?scripts/([^\s)]+?\.md)", text)}

def label(name):
    bits = []
    if "fin" in by_name[name].tags: bits.append("■ fin")
    elif not links[name]: bits.append("⚠ sans suite")
    n = len(parents.get(name, ()))
    if n > 1: bits.append(f"{n} entrées")
    return ("  " + " · ".join(bits)) if bits else ""

def link(p):
    return f"[{p.name.strip()}](scripts/{link_path(p.file)})"

lines, seen = [], set()
def walk(name, depth, cond):
    pad = "  " * depth
    c = f"  ({cond})" if cond else ""
    if name not in by_name:
        lines.append(f"{pad}- ✗ introuvable : {name}{c}")
        return
    p = by_name[name]
    if name in seen:
        lines.append(f"{pad}- ↪ {link(p)}{c}  (déjà plus haut)")
        return
    seen.add(name)
    box = "x" if p.file in checked else " "
    lines.append(f"{pad}- [{box}] {link(p)}{c}{label(name)}")
    for t, cnd in links[name]:
        walk(t, depth + 1, cnd)

walk(start, 0, "")
orphans = [n for n in by_name if n not in seen]
if orphans:
    lines += ["", "## Hors de l'arbre (aucun lien n'y mène depuis le début)", ""]
    for n in sorted(orphans, key=str.lower):
        if n not in seen:
            walk(n, 0, "")

head = ["# Passages, dans l'ordre de l'histoire", "",
        "Sur GitHub : clic sur un nom pour ouvrir le passage · [x] : passage terminé · (…) : condition du lien",
        "Dans Neovim : Entrée : ouvrir · <leader>x : cocher · za : plier une branche",
        "■ fin : passage de fin · N entrées : plusieurs passages y mènent · ↪ : déjà listé plus haut · ⚠ sans suite : aucun lien et pas de tag fin", ""]
idx.write_text("\n".join(head + lines) + "\n", encoding="utf-8", newline="\n")
print(f"_index.md : {len(seen)} passages")
if fixed:
    print("Passages complétés : " + ", ".join(fixed))
