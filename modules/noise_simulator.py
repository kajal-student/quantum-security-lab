"""
Quantum Noise Simulator
=======================
Demonstrates how realistic noise models degrade quantum circuit fidelity.
Users select a preset circuit, tune noise parameters, and observe the
statistical difference between ideal and noisy simulations.
"""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from auth.quantum_auth import build_preset_circuit, run_circuit_simulation, run_noisy_circuit, PRESET_CIRCUITS
from visualizations.charts import noise_comparison_grouped, tvd_gauge
from utils.helpers import tvd, log_experiment

matplotlib.use("Agg")

# ── Noise-type explanations ───────────────────────────────────────────────────

_NOISE_DESCRIPTIONS = {
    "Depolarizing": (
        "**Depolarizing noise** randomly replaces the qubit state with a maximally mixed state. "
        "With probability p the gate output is corrupted — replaced by a random Pauli error (X, Y, or Z) "
        "with equal probability. This is the most realistic noise model for current superconducting hardware."
    ),
    "Bit Flip": (
        "**Bit flip noise** applies an X gate (|0⟩↔|1⟩) with probability p after each gate. "
        "It models classical bit-flip errors — the simplest noise source. "
        "Pure bit flips are easier to detect and correct than full depolarizing noise."
    ),
    "Phase Flip": (
        "**Phase flip noise** applies a Z gate (|1⟩→−|1⟩) with probability p. "
        "Unlike bit flips, phase errors are invisible in the computational basis — "
        "they only appear as interference degradation. Critical for algorithms that "
        "rely on phase relationships (QFT, Grover's)."
    ),
}

_CIRCUIT_DESCRIPTIONS = {
    "Superposition (H)": (
        "1-qubit Hadamard circuit. Ideal output: 50% |0⟩, 50% |1⟩. "
        "Noise shifts these probabilities — heavier errors make one outcome more likely."
    ),
    "Bell State": (
        "2-qubit H + CNOT. Ideal: 50% |00⟩, 50% |11⟩ (maximally entangled). "
        "Noise introduces |01⟩ and |10⟩ outcomes — direct evidence of decoherence breaking entanglement."
    ),
    "GHZ State": (
        "3-qubit H + CNOT + CNOT. Ideal: 50% |000⟩, 50% |111⟩. "
        "GHZ states are extremely noise-sensitive — any single-qubit error breaks the global correlation."
    ),
    "Bit Flip (X)": (
        "1-qubit X gate. Ideal: 100% |1⟩. "
        "Noise introduces |0⟩ outcomes — clearest demonstration of error rate directly visible in results."
    ),
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _init() -> None:
    if "ns_results" not in st.session_state:
        st.session_state.ns_results = None
    if "ns_rerun_cfg" in st.session_state:
        cfg = st.session_state.pop("ns_rerun_cfg")
        st.session_state["_ns_prefill"] = cfg


def _draw_circuit(qc) -> None:
    try:
        fig = qc.draw("mpl", fold=-1)
        fig.patch.set_facecolor("#0D0D1A")
        for ax in fig.get_axes():
            ax.set_facecolor("#161629")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except Exception:
        st.code(str(qc.draw("text")), language=None)


# ── Main render ───────────────────────────────────────────────────────────────

def render_noise_simulator() -> None:
    st.markdown("## 🔧 Quantum Noise Simulator")
    st.markdown(
        "*Compare ideal quantum circuits against noise-perturbed simulations "
        "using Qiskit Aer's built-in noise models.*"
    )
    _init()

    # Pre-fill from dashboard rerun
    prefill = st.session_state.pop("_ns_prefill", {})

    st.divider()

    # ── Controls ──────────────────────────────────────────────────────────────
    st.markdown("### Experiment Configuration")
    ctrl1, ctrl2, ctrl3 = st.columns(3, gap="medium")

    with ctrl1:
        circuit_names = list(PRESET_CIRCUITS.keys())
        default_circ  = prefill.get("circuit", circuit_names[0])
        default_idx   = circuit_names.index(default_circ) if default_circ in circuit_names else 0
        circuit_name  = st.selectbox("Preset Circuit", circuit_names, index=default_idx)

    with ctrl2:
        noise_options  = ["Depolarizing", "Bit Flip", "Phase Flip"]
        default_noise  = prefill.get("noise_type", "Depolarizing")
        default_n_idx  = noise_options.index(default_noise) if default_noise in noise_options else 0
        noise_type     = st.selectbox("Noise Model", noise_options, index=default_n_idx)

    with ctrl3:
        default_level = float(prefill.get("noise_level", 0.05))
        noise_level   = st.slider(
            "Error Rate (p)",
            min_value=0.0, max_value=0.25,
            value=default_level, step=0.01,
            help="Probability of error per gate operation",
        )

    shots_col, run_col = st.columns([2, 1])
    with shots_col:
        shots = st.select_slider("Shots", [512, 1024, 2048, 4096], value=1024)
    with run_col:
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("▶ Run Simulation", type="primary", use_container_width=True)

    # Circuit description
    st.markdown(
        f'<div class="info-block">'
        f'<strong style="color:#a78bfa;">{circuit_name}</strong> — '
        f'{_CIRCUIT_DESCRIPTIONS[circuit_name]}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Noise description
    st.markdown(
        f'<div class="info-block" style="border-left-color:#ef4444;">'
        f'{_NOISE_DESCRIPTIONS[noise_type]}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Run ───────────────────────────────────────────────────────────────────
    if run:
        qc = build_preset_circuit(circuit_name)
        with st.spinner("Running ideal circuit…"):
            clean = run_circuit_simulation(qc, shots=shots)
        with st.spinner(f"Running {noise_type} noise (p={noise_level:.2f})…"):
            noisy = run_noisy_circuit(qc, noise_type, noise_level, shots=shots)

        dist = tvd(clean, noisy, shots)
        st.session_state.ns_results = {
            "circuit_name": circuit_name,
            "noise_type":   noise_type,
            "noise_level":  noise_level,
            "shots":        shots,
            "clean":        clean,
            "noisy":        noisy,
            "tvd":          dist,
            "circuit":      qc,
        }
        log_experiment(
            exp_type="Noise",
            label=f"{circuit_name} · {noise_type} p={noise_level:.2f}",
            config={"circuit": circuit_name, "noise_type": noise_type,
                    "noise_level": noise_level, "shots": shots},
            metrics={"tvd": round(dist, 4), "shots": shots,
                     "clean_states": len(clean), "noisy_states": len(noisy)},
        )

    # ── Results ───────────────────────────────────────────────────────────────
    if not st.session_state.ns_results:
        st.markdown(
            '<div style="text-align:center; padding:60px; color:#2d2d4e;">'
            'Configure and click <strong>Run Simulation</strong> to see results.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    r = st.session_state.ns_results
    st.divider()
    st.markdown(f"### Results — {r['circuit_name']} · {r['noise_type']} (p = {r['noise_level']:.2f})")

    # ── Circuit diagram ───────────────────────────────────────────────────────
    with st.expander("Circuit Diagram", expanded=False):
        _draw_circuit(r["circuit"])

    # ── Metrics row ───────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Shots",         f"{r['shots']:,}")
    m2.metric("Clean States",  len(r["clean"]))
    m3.metric("Noisy States",  len(r["noisy"]))
    m4.metric("TVD",           f"{r['tvd']:.4f}",
              help="Total Variation Distance: 0 = identical distributions, 1 = no shared probability mass")

    # ── Charts ───────────────────────────────────────────────────────────────
    chart_col, gauge_col = st.columns([3, 1], gap="large")
    with chart_col:
        st.plotly_chart(
            noise_comparison_grouped(
                r["clean"], r["noisy"], r["shots"],
                title=f"{r['circuit_name']} — Ideal vs {r['noise_type']} Noise",
            ),
            use_container_width=True,
        )
    with gauge_col:
        st.plotly_chart(tvd_gauge(r["tvd"]), use_container_width=True)
        quality = "Excellent" if r["tvd"] < 0.05 else \
                  "Good"      if r["tvd"] < 0.12 else \
                  "Degraded"  if r["tvd"] < 0.25 else "Severely Noisy"
        st.markdown(
            f'<div style="text-align:center; padding:8px; '
            f'color:{"#10b981" if r["tvd"] < 0.12 else "#ef4444"}; font-weight:600;">'
            f'Circuit quality: {quality}</div>',
            unsafe_allow_html=True,
        )

    # ── State-level comparison table ──────────────────────────────────────────
    with st.expander("State-level probability table"):
        all_states = sorted(set(r["clean"]) | set(r["noisy"]))
        rows = [
            {
                "State":       f"|{s}⟩",
                "P (clean)":   f"{r['clean'].get(s, 0) / r['shots']:.4f}",
                "P (noisy)":   f"{r['noisy'].get(s, 0) / r['shots']:.4f}",
                "Δ":           f"{(r['noisy'].get(s, 0) - r['clean'].get(s, 0)) / r['shots']:+.4f}",
            }
            for s in all_states
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Educational notes ─────────────────────────────────────────────────────
    with st.expander("📖 Understanding noise in quantum systems"):
        st.markdown(f"""
**What TVD = {r['tvd']:.4f} means**

Total Variation Distance (TVD) measures how different two probability distributions are:
- TVD = 0.00 → distributions are identical (noise had no statistical effect)
- TVD = 1.00 → distributions share no probability mass (catastrophic noise)
- Your result: TVD = **{r['tvd']:.4f}** → {
    "noise is negligible" if r['tvd'] < 0.05 else
    "minor distortion — typical for early NISQ devices" if r['tvd'] < 0.15 else
    "significant degradation — circuit depth likely exceeds coherence time" if r['tvd'] < 0.3 else
    "severe decoherence — circuit results are unreliable"
}

**Why quantum computers are noisy**

Current quantum hardware (NISQ era — Noisy Intermediate-Scale Quantum) suffers from:
1. **Gate errors** — physical gates aren't perfect unitary operations (~0.1–1% per gate)
2. **Decoherence** — qubits lose their quantum state over time (T1, T2 times)
3. **Readout errors** — measuring a qubit can be misclassified (~1–3%)
4. **Crosstalk** — adjacent qubits interfere with each other

**Noise mitigation strategies** (used in real research):
- Zero-Noise Extrapolation (ZNE)
- Probabilistic Error Cancellation (PEC)
- Symmetry verification and post-selection

*This simulation uses Qiskit Aer's noise models to approximate real hardware behavior.*
        """)

