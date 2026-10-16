import redis
r = redis.Redis(host="db", port=6379)
n = r.incr("visites")
print(f"Visite numero {n}")
