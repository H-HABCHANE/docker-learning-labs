import os
import redis

hote = os.environ.get("REDIS_HOST", "localhost")
mot_de_passe = os.environ.get("REDIS_PASSWORD")
nom = os.environ.get("NOM_APP", "Sans nom")

r = redis.Redis(host=hote, port=6379, password=mot_de_passe)
n = r.incr("visites")
print(f"[{nom}] Visite numero {n}")
