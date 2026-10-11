from pathlib import Path

dossier = Path("/data")
fichier_compteur = dossier / "compteur.txt"
fichier_html = dossier / "index.html"

if fichier_compteur.exists():
    compteur = int(fichier_compteur.read_text().strip())
else:
    compteur = 0

compteur += 1

fichier_compteur.write_text(str(compteur))

fichier_html.write_text(
    f"<h1>Nombre de visites : {compteur}</h1>\n"
)

print(f"Compteur mis à jour : {compteur}")
