from pathlib import Path
import html

entree = Path("/entree/messages.txt")
sortie = Path("/pages")
compteur_file = sortie / "compteur.txt"
index_file = sortie / "index.html"

sortie.mkdir(parents=True, exist_ok=True)

# Lire les messages du bind mount
messages = entree.read_text().splitlines()

# Compteur conservé dans le volume nommé
if compteur_file.exists():
    compteur = int(compteur_file.read_text().strip())
else:
    compteur = 0

compteur += 1
compteur_file.write_text(str(compteur))

# Générer la page HTML
liste = "\n".join(
    f"<li>{html.escape(message)}</li>"
    for message in messages
    if message.strip()
)

page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Livre d'or</title>
</head>
<body>
    <h1>Mon livre d'or</h1>
    <p>Génération numéro : {compteur}</p>
    <ul>
        {liste}
    </ul>
</body>
</html>
"""

index_file.write_text(page)

print(f"Page générée avec succès - génération {compteur}")
