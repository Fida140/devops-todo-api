# smoke_test.py - Test rapide : l'application démarre-t-elle et répond-elle ?
import json
import sys
import time
import urllib.request

# Adresse de l'application (par défaut : http://localhost:5000)
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
RESULT_FILE = "smoke-results.txt"
results = []


def get_json(path):
    """Appelle une adresse de l'API et retourne (code HTTP, contenu JSON)."""
    with urllib.request.urlopen(BASE_URL + path, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def record(name, ok, detail):
    """Enregistre le résultat d'un test et l'affiche."""
    line = f"[{'PASSED' if ok else 'FAILED'}] {name} | {detail}"
    results.append(line)
    print(line)
    return ok


def wait_for_app(max_tries=10):
    """Attend que l'application soit prête (Docker met quelques secondes à démarrer)."""
    for attempt in range(1, max_tries + 1):
        try:
            get_json("/health")
            return True
        except Exception:
            print(f"Tentative {attempt}/{max_tries} : application pas encore prete...")
            time.sleep(2)
    return False


def test_health():
    """Test 1 : /health doit répondre 200 avec status = ok."""
    try:
        status, data = get_json("/health")
        ok = status == 200 and data.get("status") == "ok"
        return record("Health check (/health)", ok, f"HTTP {status} -> {data}")
    except Exception as error:
        return record("Health check (/health)", False, f"Erreur : {error}")


def test_tasks():
    """Test 2 : /tasks doit répondre 200 avec une liste."""
    try:
        status, data = get_json("/tasks")
        ok = status == 200 and isinstance(data, list)
        return record("Liste des taches (/tasks)", ok, f"HTTP {status} -> {len(data)} tache(s)")
    except Exception as error:
        return record("Liste des taches (/tasks)", False, f"Erreur : {error}")


print(f"=== Smoke test sur {BASE_URL} ===")

if wait_for_app():
    test1 = test_health()
    test2 = test_tasks()
    all_ok = test1 and test2
else:
    record("Demarrage de l'application", False, "L'application ne repond pas")
    all_ok = False

final = "PASSED" if all_ok else "FAILED"
results.append(f"RESULTAT FINAL : {final}")
print(f"=== RESULTAT FINAL : {final} ===")

# Sauvegarde des résultats dans un fichier (sera archivé par Jenkins)
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(results) + "\n")

# Code de sortie : 0 = succès, 1 = échec (Jenkins s'en sert pour Passed/Failed)
sys.exit(0 if all_ok else 1)