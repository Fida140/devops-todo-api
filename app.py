# app.py - API To-Do simple pour le projet DevOps
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Version de l'application (sera remplie par Jenkins avec le tag vX.Y.Z)
APP_VERSION = os.environ.get("APP_VERSION", "dev")

# Liste des tâches gardée en mémoire (pas de base de données)
tasks = [
    {"id": 1, "title": "Apprendre Git", "done": True},
    {"id": 2, "title": "Apprendre Docker", "done": False},
]


@app.route("/health")
def health():
    """Vérifie que l'application fonctionne (utilisé par le smoke test)."""
    return jsonify({"status": "ok", "version": APP_VERSION})


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Retourne la liste de toutes les tâches."""
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def add_task():
    """Ajoute une nouvelle tâche."""
    data = request.get_json()
    new_task = {"id": len(tasks) + 1, "title": data["title"], "done": False}
    tasks.append(new_task)
    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>/done", methods=["PUT"])
def mark_done(task_id):
    """Marque une tâche comme terminée."""
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            return jsonify(task)
    return jsonify({"error": "Tâche introuvable"}), 404


if __name__ == "__main__":
    # 0.0.0.0 = accessible depuis l'extérieur (nécessaire pour Docker)
    app.run(host="0.0.0.0", port=5000)