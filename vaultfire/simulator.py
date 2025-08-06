"""Vaultfire reward simulation utilities."""


def simulate_passive_yield(trait_score: int, reflection_frequency: int) -> str:
    """Return a mock passive yield signal.

    The yield is a simple combination of moral trait score and the
    number of reflections submitted. Positive traits boost the base
    while frequent reflections add a compounding bonus.
    """

    base = max(trait_score, 0) * 0.1
    bonus = reflection_frequency * 0.05
    total = round(base + bonus, 2)
    return f"\U0001F506 Simulated yield: {total} pts"
