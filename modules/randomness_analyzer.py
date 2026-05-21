"""
Classical vs Quantum Randomness Analyzer
=========================================
Side-by-side comparison of NumPy's Mersenne Twister PRNG and quantum-measured
random integers produced by Qiskit Aer Hadamard circuits.
Metrics: Shannon entropy, distribution histograms, sequential independence.
"""

import numpy as np
import streamlit as st

from auth.quantum_auth import generate_quantum_random_samples
from visualizations.charts import (
    entropy_comparison_bar,
    randomness_histogram,
    sequence_scatter,
)
from utils.helpers import calculate_shannon_entropy, runs_change_ratio, log_experiment


# ── Stats computation ─────────────────────────────────────────────────────────

def _stats(arr: np.ndarray, label: str) -> dict:
    return {
        "label": label,
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": int(np.min(arr)),
        "max": int(np.max(arr)),
        "unique": int(np.unique(arr).size),
        "entropy": calculate_shannon_entropy(arr),
        "change_ratio": runs_change_ratio(arr),
    }


# ── Stats card ────────────────────────────────────────────────────────────────

def _stats_card(s: dict, color: str) -> None:
    rows = [
        ("Mean",          f"{s['mean']:.3f}"),
        ("Std Dev",       f"{s['std']:.3f}"),
        ("Min / Max",     f"{s['min']} / {s['max']}"),
        ("Unique values", f"{s['unique']}"),
        ("Change ratio",  f"{s['change_ratio']:.4f}"),
        ("Shannon H",     f"<strong style='color:{color};'>{s['entropy']:.4f} bits</strong>"),
    ]
    rows_html = "".join(
        f"<tr>"
        f"<td style='padding:5px 0; color:#475569; font-size:0.84em;'>{k}</td>"
        f"<td style='text-align:right; color:#e2e8f0; font-size:0.84em;'>{v}</td>"
        f"</tr>"
        for k, v in rows
    )
    st.markdown(
        f'<div style="background:rgba(22,22,41,0.75); border:1px solid {color}33; '
        f'border-radius:10px; padding:18px;">'
        f'<h4 style="color:{color}; margin:0 0 14px 0; font-size:0.95em;">{s["label"]}</h4>'
        f'<table style="width:100%; border-collapse:collapse;">{rows_html}</table>'
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Main render ───────────────────────────────────────────────────────────────

def render_randomness_analyzer() -> None:
    st.markdown("## 🎲 Classical vs Quantum Randomness Analyzer")
    st.markdown(
        "*Compare NumPy's deterministic PRNG against quantum-measured random numbers "
        "produced by Qiskit Aer Hadamard circuits.*"
    )

    st.divider()

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 2], gap="medium")

    with ctrl1:
        n_samples = st.slider("Sample count", 200, 2000, 512, step=100)
    with ctrl2:
        bits = st.select_slider("Bit width per sample", options=[4, 6, 8], value=8)
        max_val = 2**bits - 1
        st.caption(f"Values in [0, {max_val}] → {2**bits} possible integers")
    with ctrl3:
        st.markdown("<br>", unsafe_allow_html=True)
        generate = st.button("Generate & Compare", type="primary", use_container_width=True)

    if generate:
        with st.spinner(f"Generating {n_samples:,} classical samples…"):
            rng = np.random.default_rng()
            classical = rng.integers(0, max_val + 1, size=n_samples).astype(np.int64)

        with st.spinner(f"Generating {n_samples:,} quantum samples via Qiskit Aer…"):
            quantum = generate_quantum_random_samples(n_samples, bits_per_sample=bits)

        st.session_state["ra_classical"] = classical
        st.session_state["ra_quantum"]   = quantum
        st.session_state["ra_bits"]      = bits
        st.session_state["ra_n"]         = n_samples
        log_experiment(
            exp_type="Randomness",
            label=f"{n_samples} samples · {bits}-bit",
            config={"n_samples": n_samples, "bits": bits, "max_val": max_val},
            metrics={
                "classical_H": round(calculate_shannon_entropy(classical), 4),
                "quantum_H":   round(calculate_shannon_entropy(quantum), 4),
            },
        )

    if "ra_classical" not in st.session_state:
        st.markdown("""
        <div style="text-align:center; padding:70px 20px; color:#2d2d4e;">
            <div style="font-size:2.5em; margin-bottom:12px;">🎲</div>
            <p style="font-size:1em;">Configure parameters above and click
            <strong style="color:#7C3AED;">Generate &amp; Compare</strong>.</p>
            <p style="font-size:0.85em; color:#1e1e3a;">
                Quantum samples use a Hadamard circuit measured via Qiskit Aer.
                Classical samples use NumPy's Mersenne Twister PRNG.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    classical: np.ndarray = st.session_state["ra_classical"]
    quantum:   np.ndarray = st.session_state["ra_quantum"]
    bits_used: int        = st.session_state["ra_bits"]
    n_used:    int        = st.session_state["ra_n"]
    max_val_used          = 2**bits_used - 1

    c_stats = _stats(classical, "Classical — NumPy PRNG")
    q_stats = _stats(quantum,   "Quantum — Qiskit Aer")

    # ── Statistical summaries ─────────────────────────────────────────────────
    st.divider()
    st.markdown("### Statistical Summary")

    s_col1, s_col2 = st.columns(2, gap="medium")
    with s_col1:
        _stats_card(c_stats, "#f59e0b")
    with s_col2:
        _stats_card(q_stats, "#7C3AED")

    # ── Distribution histogram ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Distribution Comparison")
    n_bins = min(max_val_used + 1, 64)
    st.plotly_chart(randomness_histogram(classical, quantum, n_bins=n_bins), use_container_width=True)

    # ── Sequential view ───────────────────────────────────────────────────────
    n_show = min(300, n_used)
    st.plotly_chart(sequence_scatter(classical, quantum, n_show=n_show), use_container_width=True)

    # ── Entropy analysis ──────────────────────────────────────────────────────
    st.markdown("### Entropy Analysis")
    ent_chart_col, ent_delta_col = st.columns([3, 2], gap="large")

    with ent_chart_col:
        st.plotly_chart(
            entropy_comparison_bar(c_stats["entropy"], q_stats["entropy"]),
            use_container_width=True,
        )

    with ent_delta_col:
        max_possible = float(bits_used)
        diff = q_stats["entropy"] - c_stats["entropy"]
        diff_color = "#10b981" if diff >= 0 else "#ef4444"

        st.markdown("**Entropy Delta (Quantum − Classical)**")
        st.markdown(
            f'<div style="text-align:center; font-size:2.2em; color:{diff_color}; '
            f'font-family:monospace; padding:16px 0;">'
            f'{"+" if diff >= 0 else ""}{diff:.4f} bits</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**Efficiency vs theoretical max**")
        c_eff = c_stats["entropy"] / max_possible * 100
        q_eff = q_stats["entropy"] / max_possible * 100
        st.markdown(
            f"- Max possible H: **{max_possible:.2f} bits**\n"
            f"- Classical efficiency: **{c_eff:.1f}%**\n"
            f"- Quantum efficiency: **{q_eff:.1f}%**"
        )

    # ── Independence metrics ──────────────────────────────────────────────────
    st.divider()
    st.markdown("### Sequential Independence (Change Ratio)")
    st.caption(
        "Fraction of consecutive sample pairs with different values. "
        "For truly random {0…N} integers this approaches 1 − 1/N."
    )
    ind1, ind2, ind3 = st.columns(3)
    expected = 1.0 - 1.0 / (max_val_used + 1)
    ind1.metric("Classical", f"{c_stats['change_ratio']:.4f}", delta=f"{c_stats['change_ratio'] - expected:+.4f} vs expected")
    ind2.metric("Quantum",   f"{q_stats['change_ratio']:.4f}", delta=f"{q_stats['change_ratio'] - expected:+.4f} vs expected")
    ind3.metric("Expected (uniform)",  f"{expected:.4f}")

    # ── Educational expander ──────────────────────────────────────────────────
    st.divider()
    with st.expander("Understanding the comparison — detailed analysis"):
        st.markdown(f"""
**Classical PRNG — NumPy Mersenne Twister (MT19937)**
- Deterministic algorithm with period 2¹⁹⁹³⁷ − 1
- Seeded by the OS entropy pool (urandom) at startup
- Designed to pass all standard statistical randomness tests (Diehard, NIST STS)
- **Critical weakness:** if the 624-element internal state is ever recovered,
  the full past and future sequence is predictable
- Suitable for simulations; not recommended for cryptographic tokens alone

**Quantum PRNG — Qiskit Aer Hadamard Circuit**
- {bits_used} qubits placed in superposition: |+⟩ = (|0⟩ + |1⟩)/√2 per qubit
- Measurement collapses each qubit independently with exactly 50% probability
- On real quantum hardware: outcome is **physically undetermined** until measured —
  no algorithm (even in principle) can predict it
- No internal state to recover; each run is independent of all previous runs
- Suitable for cryptographic key material when run on real hardware

**Why entropy values are similar with {n_used:,} samples**

NumPy's PRNG is *engineered* to produce statistically uniform output — it passes
the same entropy tests as quantum randomness. The critical difference is in
**predictability**, not distribution shape. With {n_used:,} samples from a {bits_used}-bit
range, both sources closely approximate the {max_possible:.2f}-bit theoretical maximum.

The real quantum advantage emerges in adversarial settings: an attacker who
intercepts the generator's internal state can predict all future classical tokens
but can never predict future quantum measurements.
        """)
