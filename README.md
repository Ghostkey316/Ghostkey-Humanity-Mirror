# Vaultfire 🔥

Vaultfire is a full‑stack experiment in reflective XP systems. Users log daily reflections, react to signals, and unlock rituals as they progress.

The project ships with a Streamlit interface, backend helpers and comprehensive unit tests. It was built for the OpenAI OSS Hackathon.

## Features
- **XP system** tracking reflections, streaks and leaderboard placement.
- **Ritual unlocks** for milestones like *Ritual of Fire*, *Eyes Opened* and *Chainbreaker*.
- **Chain rituals**: three public reflections within 30 minutes grant +150 XP and contribute toward the *Signal Architect* title.
- **Signalboard** displaying live public reflections with emoji reactions and sort options.
- **Persistent reactions** stored in `reactions.json` and public reflections stored in `reflections.json`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
streamlit run vaultfire/app.py
```

### Running Tests
```bash
pytest -q
```

## Project Structure
```
vaultfire/
  app.py
  reactions.json
  reflections.json
  rituals.json
  utils.py

tests/
  test_chain_rituals.py
  test_ritual_unlocks.py

README.md
.env.example
```

## Timezone Handling
All timestamps use `datetime.now(timezone.utc)` via a helper `utcnow()` to avoid naive/aware warnings. This ensures consistent behaviour across the app and tests.

## Deployment

The app is a standard Streamlit project and can be deployed to services such as [Streamlit Community Cloud](https://streamlit.io/cloud) or any platform that can run a Python web server (e.g. Vercel with a Dockerfile).

## Contributing

Pull requests are welcome! Please run the unit tests with `pytest -q` and ensure code is formatted before submitting.

## License

This project is released under the [MIT License](LICENSE).

---
Built by `ghostkey316.eth` for the OpenAI hackathon.
