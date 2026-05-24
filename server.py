#!/usr/bin/env python3
"""
LeetCode Patterns - Flask backend
Serves the HTML and persists solved state to progress.json

Run:  python3 server.py
Then open:  http://localhost:8080
"""

import json
import os
from flask import Flask, send_from_directory, jsonify, request

app = Flask(__name__, static_folder=".")
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress.json")


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                data = json.load(f)
                # support both list and {"solved": [...]} formats
                if isinstance(data, list):
                    return data
                return data.get("solved", [])
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_progress(solved_list):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"solved": solved_list}, f, indent=2)


@app.route("/")
def index():
    return send_from_directory(".", "leetcode_patterns_v2.html")


@app.route("/api/progress", methods=["GET"])
def get_progress():
    return jsonify({"solved": load_progress()})


@app.route("/api/progress", methods=["POST"])
def set_progress():
    body = request.get_json(force=True, silent=True) or {}
    solved = body.get("solved", [])
    if not isinstance(solved, list):
        return jsonify({"error": "solved must be a list"}), 400
    # ensure all IDs are ints
    solved = [int(x) for x in solved]
    save_progress(solved)
    return jsonify({"ok": True, "saved": len(solved)})


if __name__ == "__main__":
    print("=" * 52)
    print("  LeetCode Patterns server starting...")
    print("  Open http://localhost:8080 in your browser")
    print("  Progress saved to:", os.path.abspath(PROGRESS_FILE))
    print("=" * 52)
    app.run(host="0.0.0.0", port=8080, debug=False)
