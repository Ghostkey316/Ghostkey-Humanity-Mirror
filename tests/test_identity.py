import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "src"))

from identity.bridge import generate_belief_certificate
from identity.exporter import export_certificate
from memory_graph import update_graph
from vaultfire import rewards


def test_identity_bridge_includes_tags_and_reflections():
    update_graph("I was honest and kind today.")
    rewards.calculate("I was honest and kind today.")

    cert = generate_belief_certificate(
        "ghostkey316.eth", "bpow20.cb.id", biometric_hash="biohash"
    )
    assert cert["ens"] == "ghostkey316.eth"
    assert cert["cb_id"] == "bpow20.cb.id"
    assert cert["biometric_hash"] == "biohash"
    assert cert["recent_reflections"]
    assert "reward_signal" in cert


def test_exporter_formats_and_writes_file():
    update_graph("Another honest reflection full of compassion.")
    rewards.calculate("Another honest reflection full of compassion.")

    cert = generate_belief_certificate("ghostkey316.eth", "bpow20.cb.id")
    path = export_certificate(cert)
    assert os.path.exists(path)
    with open(path) as f:
        data = json.load(f)

    assert data["integrity_level"] in {"low", "medium", "high", "legendary"}
    assert "traits_summary" in data
    assert "reward_preview" in data
    assert "vaultfire_output" in data

    os.remove(path)
