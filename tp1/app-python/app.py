import datetime
import platform

print("Salut depuis Python", platform.python_version())
print("Image construite le :", open("build-info.txt").read().strip())
print("Conteneur lancé le  :", datetime.datetime.now())
