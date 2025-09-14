#!/usr/bin/env python3
import requests
import json
import datetime
from tabulate import tabulate

# URL de base
BASE_URL = "http://63.35.53.134:8085/api/v1/movies/"

# Fichier de log
log_file = f"api_test_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# Stocker les résultats
results = []

def log_result(test_name, success, status_code=None, response_text=None):
    entry = {
        "Test": test_name,
        "Status": "✅" if success else "❌",
        "HTTP Code": status_code,
        "Response": response_text
    }
    results.append(entry)
    print(f"{test_name}: {entry['Status']} (HTTP {status_code})")

# 1️⃣ GET all movies
try:
    r = requests.get(BASE_URL, headers={"accept": "application/json"})
    log_result("GET all movies", r.status_code == 200, r.status_code, r.text)
except Exception as e:
    log_result("GET all movies", False)

# 2️⃣ POST a new movie
new_movie = {
    "name": "Test Movie",
    "plot": "Test Plot",
    "genres": ["Action"],
    "casts_id": [0]
}
movie_id = None
try:
    r = requests.post(BASE_URL, headers={"accept": "application/json", "Content-Type": "application/json"}, data=json.dumps(new_movie))
    log_result("POST new movie", r.status_code in [200,201], r.status_code, r.text)
    if r.status_code in [200,201]:
        movie_id = r.json().get("id")
except Exception as e:
    log_result("POST new movie", False)

# 3️⃣ GET movie by ID
if movie_id:
    try:
        r = requests.get(f"{BASE_URL}{movie_id}/", headers={"accept": "application/json"})
        log_result("GET movie by ID", r.status_code == 200, r.status_code, r.text)
    except Exception as e:
        log_result("GET movie by ID", False)

# 4️⃣ PUT update movie
updated_movie = {
    "name": "Test Movie Updated",
    "plot": "Updated Plot",
    "genres": ["Action", "Drama"],
    "casts_id": [0]
}
if movie_id:
    try:
        r = requests.put(f"{BASE_URL}{movie_id}/", headers={"accept": "application/json", "Content-Type": "application/json"}, data=json.dumps(updated_movie))
        log_result("PUT update movie", r.status_code == 200, r.status_code, r.text)
    except Exception as e:
        log_result("PUT update movie", False)

# 5️⃣ DELETE movie
if movie_id:
    try:
        r = requests.delete(f"{BASE_URL}{movie_id}/", headers={"accept": "application/json"})
        log_result("DELETE movie", r.status_code in [200,204], r.status_code, r.text)
    except Exception as e:
        log_result("DELETE movie", False)

# Affichage d'un tableau récapitulatif
table = [[res["Test"], res["Status"], res["HTTP Code"]] for res in results]
print("\n=== API Test Summary ===")
print(tabulate(table, headers=["Test", "Status", "HTTP Code"], tablefmt="grid"))

# Écriture du log complet
with open(log_file, "w") as f:
    f.write(tabulate(table, headers=["Test", "Status", "HTTP Code"], tablefmt="grid"))
    f.write("\n\nFull response log:\n")
    for entry in results:
        f.write(json.dumps(entry, indent=2))
        f.write("\n")

print(f"\n✅ Tests terminés. Logs sauvegardés dans {log_file}")
