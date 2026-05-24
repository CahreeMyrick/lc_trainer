#!/usr/bin/env python3
"""
LeetCode Patterns - Flask backend
Persistent trainer backend

Run:
    python3 server.py

Open:
    http://localhost:8080
"""

import json
import os
from flask import Flask, send_from_directory, jsonify, request

app = Flask(__name__, static_folder=".")

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "progress.json")


DEFAULT_PROGRESS = {
    "userRating": 1200,
    "solved": [],
    "attempts": {},
    "settings": {
        "minRating": 1200,
        "maxRating": 1600,
        "topics": [],
        "mode": "incremental"
    }
}


def load_progress():
    if not os.path.exists(DATA_FILE):
        return DEFAULT_PROGRESS.copy()

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        merged = DEFAULT_PROGRESS.copy()
        merged.update(data)

        if "settings" not in merged:
            merged["settings"] = DEFAULT_PROGRESS["settings"]

        if "attempts" not in merged:
            merged["attempts"] = {}

        if "solved" not in merged:
            merged["solved"] = []

        if "userRating" not in merged:
            merged["userRating"] = 1200

        return merged

    except (json.JSONDecodeError, IOError):
        return DEFAULT_PROGRESS.copy()


def save_progress(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def index():
    return send_from_directory(".", "leetcode_patterns.html")


@app.route("/api/progress", methods=["GET"])
def get_progress():
    return jsonify(load_progress())


@app.route("/api/progress", methods=["POST"])
def set_progress():

    body = request.get_json(force=True, silent=True)

    if not isinstance(body, dict):
        return jsonify({"error": "invalid json"}), 400

    progress = load_progress()

    if "userRating" in body:
        progress["userRating"] = int(body["userRating"])

    if "solved" in body:
        if not isinstance(body["solved"], list):
            return jsonify({"error": "solved must be list"}), 400

        progress["solved"] = [int(x) for x in body["solved"]]

    if "attempts" in body:
        if not isinstance(body["attempts"], dict):
            return jsonify({"error": "attempts must be dict"}), 400

        progress["attempts"] = body["attempts"]

    if "settings" in body:
        if not isinstance(body["settings"], dict):
            return jsonify({"error": "settings must be dict"}), 400

        progress["settings"] = body["settings"]

    save_progress(progress)

    return jsonify({
        "ok": True,
        "userRating": progress["userRating"],
        "solvedCount": len(progress["solved"])
    })


@app.route("/api/attempt", methods=["POST"])
def add_attempt():

    body = request.get_json(force=True, silent=True)

    if not isinstance(body, dict):
        return jsonify({"error": "invalid json"}), 400

    problem_id = str(body.get("problemId"))

    if not problem_id:
        return jsonify({"error": "problemId required"}), 400

    progress = load_progress()

    if problem_id not in progress["attempts"]:
        progress["attempts"][problem_id] = []

    progress["attempts"][problem_id].append({
        "timestamp": body.get("timestamp"),
        "solved": body.get("solved"),
        "timeMinutes": body.get("timeMinutes"),
        "difficulty": body.get("difficulty"),
        "ratingChange": body.get("ratingChange")
    })

    save_progress(progress)

    return jsonify({
        "ok": True,
        "attempts": len(progress["attempts"][problem_id])
    })


if __name__ == "__main__":

    print("=" * 60)
    print(" LeetCode Patterns Trainer Server")
    print(" Open: http://localhost:8080")
    print(" Data file:", os.path.abspath(DATA_FILE))
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )