# Rioctober : écriture de « 17 octobre »

Une histoire interactive écrite à plusieurs. Chaque passage est un petit fichier texte
dans [`scripts/`](scripts/), et l'arbre complet de l'histoire est dans [`_index.md`](_index.md).

**▶ Jouer à la dernière version : https://omarmelade.github.io/redesigned-couscous/**
(mise à jour toute seule une ou deux minutes après chaque modification)

- [_index.md](_index.md) : l'arbre de l'histoire depuis le début, clique sur un nom pour ouvrir le passage.
- [avancement.md](avancement.md) : ce qui est écrit, en cours ou encore vide.

---

## Écrire depuis le navigateur (sans rien installer)

### Modifier un passage

1. Ouvre [_index.md](_index.md) et clique sur le passage.
2. Clique sur le **crayon ✏️** en haut à droite du fichier.
3. Écris sous `## Texte`. Tu peux mettre tes idées sous `## Notes` : elles n'apparaissent pas dans le jeu.
4. Clique sur **Commit changes…** (en vert), écris en une phrase ce que tu as changé, puis valide.

C'est enregistré. L'index, l'avancement et la version jouable se mettent à jour tout seuls.

> Astuce : appuie sur la touche **.** (point) sur la page du dépôt pour ouvrir un éditeur plus confortable
> dans le navigateur, avec tous les fichiers à gauche. Pour enregistrer, va dans l'icône
> « Source Control » à gauche, écris un message, puis **Commit & Push**.

### Ajouter un choix et un nouveau passage

1. Dans le passage de départ, sous `## Liens`, ajoute une ligne `[[Nom du nouveau passage]]`.
2. Va dans le dossier [`scripts/`](scripts/), clique sur **Add file → Create new file**.
3. Nomme le fichier sans accents ni espaces, par exemple `vous-fuyez-par-le-metro.md`.
4. Copie le contenu de [modele-passage.md](modele-passage.md) et remplace la ligne `passage:`
   par le nom **exact** utilisé dans le lien, entre guillemets : `passage: "Nom du nouveau passage"`.
5. Écris le texte, puis **Commit changes…**.

Si tu oublies l'en-tête, ce n'est pas grave : le fichier est complété automatiquement,
et le nom du passage est pris dans le nom du fichier.

### Marquer un passage comme terminé

Dans [_index.md](_index.md), clique sur le crayon et remplace `- [ ]` par `- [x]` sur la ligne du passage.

### Les règles à garder en tête

- Ne touche pas à la partie entre les deux lignes `---` en haut des fichiers, sauf pour ajouter un tag
  (par exemple `tags: ["fin"]` pour un passage qui termine l'histoire).
- Les lignes `→` sous les liens servent juste à naviguer : elles sont refaites automatiquement.
- Un lien `[[...]]` doit avoir exactement le même nom que la ligne `passage:` du passage visé.
- Si deux personnes modifient le même fichier en même temps, GitHub le signale : il suffit de recopier son texte
  dans la dernière version.
- Tout est gardé : l'onglet **History** d'un fichier permet de retrouver n'importe quelle ancienne version.

---

## Pour travailler en local (Neovim)

- `story_lib.py` : lecture des passages, partagée par les trois scripts.
- `index.py` : reconstruit `_index.md` (cases cochées gardées), complète les passages sans en-tête et refait les lignes `→`.
- `avancement.py` : écrit `avancement.md`.
- `build.py` : `python3 build.py` crée `export.twee`, à importer dans Twine.
- `_story.twee` : titre et réglages Twine (ne pas toucher).
- `.github/workflows/histoire.yml` : à chaque envoi sur `main`, lance `index.py` et `avancement.py`,
  enregistre le résultat, puis publie la version jouable (Tweego + Harlowe 3.3.9) sur GitHub Pages.

Pense à faire `git pull` avant d'écrire : l'action GitHub ajoute ses propres mises à jour.

Dans Neovim : `nvim -S .nvim.lua _index.md` (ou juste `nvim _index.md` si `vim.o.exrc = true` est dans ta config).
- `Entrée` sur un chemin ouvre le passage, `Retour arrière` revient au précédent.
- À l'ouverture d'un passage, le curseur est déjà sous `## Texte`.
- Dans `_index.md`, `<leader>x` coche ou décoche la ligne, `za` plie ou déplie une branche.
- Chaque sauvegarde d'un passage met l'index à jour tout seul.
- `:Index` reconstruit et rouvre l'arbre, `:Build` enregistre tout et crée `export.twee`.
