#!/usr/bin/env python3
"""Rassemble _story.twee + scripts/*.md en un fichier .twee importable dans Twine.

Usage : python3 build.py            -> écrit export.twee
La section Notes n'est pas exportée. Le fichier .twee d'origine n'est jamais modifié.
"""
import json
from story_lib import root, load_all, clean_links

def escape(name):
    name = name.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("{", "\\{").replace("}", "\\}")
    if name[:1] == " ": name = "\\" + name
    if name[-1:] == " ": name = name[:-1] + "\\ "
    return name

parts = [(root / "_story.twee").read_text(encoding="utf-8").replace("\r\n", "\n").rstrip("\n")]
for p in load_all():
    liens = "\n".join(p.liens()).strip("\n")
    body = clean_links("\n".join(x for x in (p.texte(), liens) if x))
    head = ":: " + escape(p.name)
    if p.tags: head += " [" + " ".join(p.tags) + "]"
    head += " " + json.dumps({"position": p.meta["position"], "size": p.meta["size"]}, separators=(",", ":"))
    parts.append(head + "\n" + body)

(root / "export.twee").write_text("\n\n\n".join(parts) + "\n", encoding="utf-8", newline="\n")
print(f"export.twee : {len(parts) - 1} passages")
