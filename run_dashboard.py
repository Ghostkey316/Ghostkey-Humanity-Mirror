"""Flask server to preview Humanity Mirror dashboard."""

from flask import Flask, jsonify, send_from_directory

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from memory_graph import get_memory_graph
from vaultfire.rewards import get_last_signal
from vaultfire.simulator import simulate_passive_yield

app = Flask(__name__, static_folder="dashboard")


@app.route("/")
def index():
    return send_from_directory("dashboard", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("dashboard", path)


@app.route("/data")
def data():
    graph = get_memory_graph()
    integrity_score = sum(node["score"] for node in graph)

    trait_cloud = {}
    for node in graph:
        for trait in node["traits"]:
            trait_cloud[trait] = trait_cloud.get(trait, 0) + 1

    frequency = len(graph)
    vaultfire_signal = get_last_signal() or simulate_passive_yield(
        integrity_score, frequency
    )

    return jsonify(
        {
            "reflections": graph,
            "integrity_score": integrity_score,
            "trait_cloud": trait_cloud,
            "vaultfire_yield": vaultfire_signal,
        }
    )


if __name__ == "__main__":
    app.run()
