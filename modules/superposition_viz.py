"""
Superposition & State Visualizer
=================================
Interactive single-qubit state explorer with:
  - 2D Bloch-sphere cross-section (practical alternative to 3D)
  - Gate-effect comparison (before / after)
  - Born-rule measurement simulation via Qiskit Aer
  - Comprehensive gate reference panel
"""

import math
import streamlit as st
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from visualizations.charts import state_vector_2d, state_probability_bars, measurement_sim_bars
from utils.helpers import state_to_bloch, bloch_from_angles, apply_gate_bloch, bloch_to_probs

_SIM = AerSimulator()

# ── Gate knowledge base ───────────────────────────────────────────────────────

_GATES: dict[str, dict] = {
    "H": {
        "full_name": "Hadamard Gate",
        "purpose":   "Creates equal superposition from any basis state.",
        "intuition": "A perfectly balanced quantum coin-flip. Takes a definite |0⟩ or |1⟩ "
                     "into a state where both outcomes are equally probable. "
                     "Applied twice, it undoes itself (H² = I).",
        "matrix":    "1/√2 · ⎡ 1  1 ⎤\n        ⎣ 1 -1 ⎦",
        "actions":   [
            ("|0⟩", "|+⟩ = (|0⟩ + |1⟩)/√2", "P(0) = P(1) = 0.5"),
            ("|1⟩", "|−⟩ = (|0⟩ − |1⟩)/√2", "P(0) = P(1) = 0.5"),
        ],
        "uses":  ["Quantum random number generation", "Grover's search algorithm",
                  "Quantum Fourier Transform", "BB84 quantum key distribution"],
        "color": "#a78bfa",
    },
    "X": {
        "full_name": "Pauli-X Gate (NOT)",
        "purpose":   "Flips the qubit: |0⟩ ↔ |1⟩.",
        "intuition": "The simplest gate — the quantum NOT. A π-rotation around the X-axis "
                     "of the Bloch sphere. No phase side-effects; purely a bit flip.",
        "matrix":    "⎡ 0  1 ⎤\n⎣ 1  0 ⎦",
        "actions":   [
            ("|0⟩", "|1⟩", "Always measures 1"),
            ("|1⟩", "|0⟩", "Always measures 0"),
        ],
        "uses":  ["State initialisation", "Grover diffuser", "Error-correction ancilla reset"],
        "color": "#10b981",
    },
    "Y": {
        "full_name": "Pauli-Y Gate",
        "purpose":   "Combined bit flip and imaginary phase flip.",
        "intuition": "Rotates the Bloch sphere by π around the Y-axis. Like X, it flips the "
                     "bit, but it also multiplies the amplitude by ±i. The phase doesn't "
                     "change measurement probabilities directly, but matters for interference.",
        "matrix":    "⎡ 0  −i ⎤\n⎣ i   0 ⎦",
        "actions":   [
            ("|0⟩", "i|1⟩", "Measures 1 (phase i unobservable)"),
            ("|1⟩", "−i|0⟩", "Measures 0 (phase −i unobservable)"),
        ],
        "uses":  ["SU(2) rotation decomposition", "Quantum error models", "State preparation with phase"],
        "color": "#f59e0b",
    },
    "Z": {
        "full_name": "Pauli-Z Gate (Phase Flip)",
        "purpose":   "Applies a phase flip: |1⟩ → −|1⟩, |0⟩ unchanged.",
        "intuition": "Invisible in the computational basis — |0⟩ and |1⟩ look identical "
                     "before and after. But in the Hadamard (±) basis it flips |+⟩ ↔ |−⟩. "
                     "Used to control quantum interference patterns.",
        "matrix":    "⎡ 1   0 ⎤\n⎣ 0  −1 ⎦",
        "actions":   [
            ("|0⟩", "|0⟩", "Unchanged — still measures 0"),
            ("|1⟩", "−|1⟩", "Phase flipped — still measures 1"),
        ],
        "uses":  ["Phase kickback", "Deutsch-Jozsa algorithm", "Oracle construction", "QFT phases"],
        "color": "#38bdf8",
    },
    "CNOT": {
        "full_name": "CNOT (Controlled-NOT) Gate",
        "purpose":   "Flips the target qubit only when the control qubit is |1⟩.",
        "intuition": "The entanglement engine. With a superposed control (H first), the "
                     "target becomes correlated — measuring one qubit instantly determines "
                     "the other. This is the core of Bell states and quantum teleportation.",
        "matrix":    "⎡ 1 0 0 0 ⎤\n⎢ 0 1 0 0 ⎥\n⎢ 0 0 0 1 ⎥\n⎣ 0 0 1 0 ⎦",
        "actions":   [
            ("|00⟩", "|00⟩", "Control=0 → no flip"),
            ("|10⟩", "|11⟩", "Control=1 → target flips"),
        ],
        "uses":  ["Bell state preparation", "Quantum teleportation", "Error correction", "GHZ states"],
        "color": "#34d399",
    },
}


# ── Measurement simulation helper ─────────────────────────────────────────────

def _prepare_state_circuit(state_name: str, theta: float) -> QuantumCircuit:
    """Return a 1-qubit circuit that prepares the specified state before measurement."""
    qc = QuantumCircuit(1, 1)
    if state_name == "|0⟩":
        pass
    elif state_name == "|1⟩":
        qc.x(0)
    elif state_name == "|+⟩":
        qc.h(0)
    elif state_name == "|−⟩":
        qc.x(0)
        qc.h(0)
    elif state_name == "Custom (θ)":
        qc.ry(theta, 0)
    qc.measure(0, 0)
    return qc


# ── Gate reference card ───────────────────────────────────────────────────────

def _gate_card(name: str, info: dict) -> None:
    color = info["color"]
    actions_html = "".join(
        f"<tr>"
        f"<td style='padding:3px 10px 3px 0; color:#64748b; font-family:monospace;'>{inp}</td>"
        f"<td style='color:{color}; font-family:monospace;'>→ {out}</td>"
        f"<td style='color:#475569; font-size:0.82em; padding-left:12px;'>{note}</td>"
        f"</tr>"
        for inp, out, note in info["actions"]
    )
    uses_html = " · ".join(
        f'<span style="background:rgba(255,255,255,0.04); border:1px solid #2d2d4e; '
        f'border-radius:4px; padding:2px 8px; font-size:0.78em; color:#64748b;">{u}</span>'
        for u in info["uses"]
    )
    st.markdown(
        f'<div style="background:rgba(22,22,41,0.8); border:1px solid {color}44; '
        f'border-left:4px solid {color}; border-radius:8px; padding:18px; margin-bottom:12px;">'
        f'<div style="display:flex; align-items:baseline; gap:10px; margin-bottom:8px;">'
        f'<span style="font-size:1.3em; font-weight:700; color:{color}; font-family:monospace;">{name}</span>'
        f'<span style="color:#94a3b8; font-size:0.88em;">{info["full_name"]}</span>'
        f'</div>'
        f'<p style="color:#94a3b8; font-size:0.86em; margin:0 0 10px 0; line-height:1.5;">{info["intuition"]}</p>'
        f'<div style="display:flex; gap:24px; flex-wrap:wrap;">'
        f'<div>'
        f'<div style="color:#475569; font-size:0.75em; margin-bottom:4px; letter-spacing:0.05em;">MATRIX</div>'
        f'<pre style="color:{color}; font-size:0.82em; margin:0; line-height:1.5;">{info["matrix"]}</pre>'
        f'</div>'
        f'<div>'
        f'<div style="color:#475569; font-size:0.75em; margin-bottom:4px; letter-spacing:0.05em;">ACTION</div>'
        f'<table style="border-collapse:collapse;">{actions_html}</table>'
        f'</div>'
        f'</div>'
        f'<div style="margin-top:10px;">'
        f'<span style="color:#475569; font-size:0.75em; letter-spacing:0.05em;">USE CASES&nbsp;</span>'
        f'{uses_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Main render ───────────────────────────────────────────────────────────────

def render_superposition_viz() -> None:
    st.markdown("## 🌀 Superposition & State Visualizer")
    st.markdown(
        "*Single-qubit state explorer with a 2D Bloch-sphere cross-section, "
        "gate-transform visualization, and Born-rule measurement simulation via Qiskit Aer.*"
    )

    tab_explorer, tab_sim, tab_gates = st.tabs([
        "State Explorer", "Measurement Simulation", "Gate Reference"
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 1: Interactive State Explorer
    # ─────────────────────────────────────────────────────────────────────────
    with tab_explorer:
        st.markdown(
            "Select an initial qubit state, optionally apply a gate, and observe "
            "how the state vector moves on the 2D Bloch-sphere cross-section."
        )
        st.markdown("""
        <div class="info-block">
            The diagram shows the <strong>xz-plane</strong> cross-section of the Bloch sphere.
            The state vector's vertical position encodes measurement probabilities:
            pointing up (|0⟩) = 100% chance of 0; pointing right (|+⟩) = 50/50.
        </div>
        """, unsafe_allow_html=True)

        ctrl_col, viz_col = st.columns([1, 2], gap="large")

        with ctrl_col:
            state_options = ["|0⟩", "|1⟩", "|+⟩", "|−⟩", "Custom (θ)"]
            init_state = st.selectbox("Initial state", state_options, key="sv_init")

            theta = 0.0
            if init_state == "Custom (θ)":
                theta_deg = st.slider(
                    "Polar angle θ (degrees)",
                    0, 180, 90,
                    help="θ = 0° → |0⟩, θ = 90° → |+⟩, θ = 180° → |1⟩",
                )
                theta = math.radians(theta_deg)

            gate_options = ["None", "H", "X", "Y", "Z"]
            gate = st.selectbox("Apply gate", gate_options, key="sv_gate")

            st.divider()

            # Compute Bloch vectors
            if init_state == "Custom (θ)":
                bloch_i = bloch_from_angles(theta, phi=0.0)
            else:
                bloch_i = state_to_bloch(init_state)

            p0_i, p1_i = bloch_to_probs(bloch_i[2])

            st.markdown("**Before gate**")
            st.metric("|P(|0⟩)|", f"{p0_i:.4f}")
            st.metric("|P(|1⟩)|", f"{p1_i:.4f}")

            bloch_f = None
            if gate != "None":
                bloch_f = apply_gate_bloch(gate, *bloch_i)
                p0_f, p1_f = bloch_to_probs(bloch_f[2])
                st.markdown(f"**After {gate}**")
                st.metric("P(|0⟩)", f"{p0_f:.4f}", delta=f"{p0_f - p0_i:+.4f}")
                st.metric("P(|1⟩)", f"{p1_f:.4f}", delta=f"{p1_f - p1_i:+.4f}")

        with viz_col:
            label_i = f"{init_state}" + ("" if gate == "None" else "  (before)")
            label_f = f"After {gate}({init_state})"

            st.plotly_chart(
                state_vector_2d(bloch_i, bloch_f or None, label_i, label_f),
                use_container_width=True,
            )

            if gate != "None":
                p0_f, p1_f = bloch_to_probs(bloch_f[2])
                st.plotly_chart(
                    state_probability_bars(p0_i, p1_i, p0_f, p1_f, init_state, f"{gate}({init_state})"),
                    use_container_width=True,
                )
            else:
                st.plotly_chart(
                    state_probability_bars(p0_i, p1_i, label_init=init_state),
                    use_container_width=True,
                )

        # Gate intuition blurb
        if gate != "None":
            g_info = _GATES[gate]
            st.markdown(
                f'<div class="info-block">'
                f'<strong style="color:{g_info["color"]};">{gate} — {g_info["full_name"]}</strong><br>'
                f'{g_info["intuition"]}'
                f'</div>',
                unsafe_allow_html=True,
            )

        with st.expander("📖 How to read this diagram"):
            st.markdown("""
**The 2D diagram is the xz-plane slice of the Bloch sphere.**

Every single-qubit pure state can be written as:

`|ψ⟩ = cos(θ/2)|0⟩ + eⁱᵠ sin(θ/2)|1⟩`

where θ (polar angle) and φ (azimuthal angle) determine the point on the sphere.
This diagram fixes φ = 0 and shows θ — sufficient for real-amplitude states (H, X, Y, Z applied to |0⟩).

**Probabilities from z-coordinate:**
- P(|0⟩) = (1 + z) / 2
- P(|1⟩) = (1 − z) / 2

So the north pole (z=+1) always yields 0, the south pole always yields 1,
and any equatorial point (z=0) gives 50/50.
            """)

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 2: Born-rule measurement simulation
    # ─────────────────────────────────────────────────────────────────────────
    with tab_sim:
        st.markdown(
            "Prepare a single-qubit state and measure it many times. "
            "The measured histogram should converge to the theoretical Born-rule probabilities."
        )

        sim_l, sim_r = st.columns([1, 2], gap="large")
        with sim_l:
            sim_state = st.selectbox("State to prepare", ["|0⟩", "|1⟩", "|+⟩", "|−⟩", "Custom (θ)"], key="sv_sim_state")
            sim_theta_deg = 90
            sim_theta = 0.0
            if sim_state == "Custom (θ)":
                sim_theta_deg = st.slider("θ (degrees)", 0, 180, 90, key="sv_sim_theta")
                sim_theta = math.radians(sim_theta_deg)

            sim_shots = st.select_slider("Measurement shots", [64, 128, 256, 512, 1024, 2048], value=512, key="sv_shots")
            run_sim = st.button("Measure", type="primary", use_container_width=True)

        with sim_r:
            if run_sim:
                with st.spinner("Running Qiskit Aer measurement simulation…"):
                    qc = _prepare_state_circuit(sim_state, sim_theta)
                    result = _SIM.run(qc, shots=sim_shots).result()
                    counts = result.get_counts()

                # Theoretical probabilities
                if sim_state == "|0⟩":
                    p0_th, p1_th = 1.0, 0.0
                elif sim_state == "|1⟩":
                    p0_th, p1_th = 0.0, 1.0
                elif sim_state in ("|+⟩", "|−⟩"):
                    p0_th, p1_th = 0.5, 0.5
                else:
                    p0_th = math.cos(sim_theta / 2) ** 2
                    p1_th = math.sin(sim_theta / 2) ** 2

                st.plotly_chart(
                    measurement_sim_bars(counts, sim_shots, p0_th, p1_th),
                    use_container_width=True,
                )

                measured_0 = counts.get("0", 0) / sim_shots
                measured_1 = counts.get("1", 0) / sim_shots
                deviation  = abs(measured_0 - p0_th)
                st.markdown(
                    f"**Theory:** P(|0⟩) = {p0_th:.4f}, P(|1⟩) = {p1_th:.4f} &nbsp;|&nbsp; "
                    f"**Measured deviation:** {deviation:.4f}  ({'↓ try more shots' if deviation > 0.05 else '✓ close'})"
                )
            else:
                st.markdown(
                    '<div style="color:#2d2d4e; padding:60px 20px; text-align:center;">'
                    'Select a state and click <strong>Measure</strong> to run the simulation.'
                    '</div>',
                    unsafe_allow_html=True,
                )

        with st.expander("📖 The Born Rule — why this works"):
            st.markdown("""
**The Born rule** states that for state |ψ⟩ = α|0⟩ + β|1⟩:

- P(measuring |0⟩) = |α|²
- P(measuring |1⟩) = |β|²

This is the **foundational postulate** of quantum measurement — not derivable from anything more basic.

Running many shots lets the empirical frequency converge to these theoretical values
(law of large numbers). With 64 shots you see noisy histograms; with 2048 shots
the bars closely match theory. This is exactly what quantum hardware demonstrates.

*Qiskit Aer simulates this by sampling from the exact quantum probability distribution.*
            """)

    # ─────────────────────────────────────────────────────────────────────────
    # Tab 3: Gate reference panel
    # ─────────────────────────────────────────────────────────────────────────
    with tab_gates:
        st.markdown(
            "Complete reference for all gates used in this lab — "
            "purpose, matrix, state-action table, and typical use cases."
        )
        for name, info in _GATES.items():
            _gate_card(name, info)

