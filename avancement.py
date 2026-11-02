#!/usr/bin/env python3
"""Calcule l'avancement des passages et l'écrit dans avancement.md.

Usage : python3 avancement.py
Ne lit que la taille des sections, jamais leur contenu.
- Vide     : section Texte vide
- En cours : Texte présent, passage non coché dans _index.md
- Écrit    : passage coché [x] dans _index.md
"""
import re
from story_lib import root, load_all, link_path

idx = (root / "_index.md").read_text(encoding="utf-8") if (root / "_index.md").exists() else ""
coche = {m.group(2).replace("%20", " "): m.group(1) in "xX"
         for m in re.finditer(r"- \[( |x|X)\] (?:\[[^\]]*\]\()?scripts/([^\s)]+?\.md)", idx)}

rows = []
for p in load_all():
    taille = len(p.texte().strip())
    liens = sum(1 for l in p.liens() if l.strip())
    statut = "Écrit" if coche.get(p.file) else ("En cours" if taille else "Vide")
    rows.append((statut, p.name.strip(), ", ".join(p.tags), taille, liens, p.file))

ordre = {"En cours": 0, "Vide": 1, "Écrit": 2}
rows.sort(key=lambda r: (ordre[r[0]], r[1].lower()))
n = {s: sum(r[0] == s for r in rows) for s in ordre}
out = [f"Total : {len(rows)} passages · Écrit {n['Écrit']} · En cours {n['En cours']} · Vide {n['Vide']}", "",
       "| Passage | Statut | Tags | Texte (caractères) | Liens |", "| --- | --- | --- | --- | --- |"]
out += [f"| [{p}](scripts/{link_path(f)}) | {s} | {t} | {c} | {l} |" for s, p, t, c, l, f in rows]
(root / "avancement.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print(out[0])
