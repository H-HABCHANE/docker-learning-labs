import os
import redis
from flask import Flask

VERSION = "2"
NOM = os.environ.get("NOM_APP", "Sans nom")

r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=6379,
    password=os.environ.get("REDIS_PASSWORD"),
)

app = Flask(__name__)

@app.route("/")
def accueil():
    n = r.incr("visites")
    return f"[{NOM}] version {VERSION} - visite numero {n}\n"

# 0.0.0.0 = accepter les connexions venant de l'exterieur du conteneur
app.run(host="0.0.0.0", port=5000)
