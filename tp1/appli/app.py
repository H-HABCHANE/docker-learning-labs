
import datetime, os
print("=== Fiche de l'appli ===")
print("Version      :", open("version.txt").read().strip())
print("Construite le:", open("build-info.txt").read().strip())
print("Lancée le    :", datetime.datetime.now())
print("Dossier      :", os.getcwd())
