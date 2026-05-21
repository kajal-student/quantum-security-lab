"""
Quantum Circuit Playground
==========================
Interactive gate-by-gate circuit builder backed by Qiskit Aer.
Includes a per-gate knowledge panel, experiment logging, and simulation charts.
"""

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from qiskit import QuantumCircuit

from auth.quantum_auth import run_circuit_simulation
from visualizations.charts import measurement_bar_chart, probability_chart
from utils.helpers import log_experiment

matplotlib.use("Agg")


# ── Gate knowledge base ───────────────────────────────────────────────────────

_GATE_KB: dict[str, dict] = {
    "H": {
        "full_name": "Hadamard Gate",
        "purpose":   "Creates equal superposition (50/50) from any basis state.",
        "intuition": "Think of it as a quantum coin flip. |0⟩ → (|0⟩+|1⟩)/√2. "
                     "Applied twice it cancels: H·H = I. The most frequently used gate in quantum algorithms.",
        "matrix":    "1/√2 · [[1, 1], [1, -1]]",
        "actions":   "|0⟩ → |+⟩   |1⟩ → |−⟩",
        "uses":      "QRNGs · Grover's search · QFT · BB84",
        "color":     "#a78bfa",
    },
    "X": {
        "full_name": "Pauli-X (NOT) Gate",
        "purpose":   "Bit flip: |0⟩ ↔ |1⟩.",
        "intuition": "The quantum NOT gate — a π-rotation around the X-axis. "
                     "No phase side-effect. Deterministic in the computational basis.",
        "matrix":    "[[0, 1], [1, 0]]",
        "actions":   "|0⟩ → |1⟩   |1⟩ → |0⟩",
        "uses":      "State init · Grover diffuser · error correction ancilla",
        "color":     "#10b981",
    },
    "Y": {
        "full_name": "Pauli-Y Gate",
        "purpose":   "Combined bit flip and imaginary phase flip.",
        "intuition": "π-rotation around Y-axis. Bit flip + phase ±i. Phase doesn't affect "
                     "measurement probability but matters for interference cancellation.",
        "matrix":    "[[0, -i], [i, 0]]",
        "actions":   "|0⟩ → i|1⟩   |1⟩ → -i|0⟩",
        "uses":      "Error models · SU(2) decomposition · phase-aware state prep",
        "color":     "#f59e0b",
    },
    "Z": {
        "full_name": "Pauli-Z Gate (Phase Flip)",
        "purpose":   "Phase flip: |1⟩ → −|1⟩, |0⟩ unchanged.",
        "intuition": "Invisible in computational-basis measurement — both |0⟩ and |1⟩ "
                     "look the same before and after. Critical for controlling quantum "
                     "interference (phase kickback technique).",
        "matrix":    "[[1, 0], [0, -1]]",
        "actions":   "|0⟩ → |0⟩   |1⟩ → −|1⟩",
        "uses":      "Phase kickback · Deutsch-Jozsa · QFT phase rotations",
        "color":     "#38bdf8",
    },
    "CNOT": {
        "full_name": "CNOT (Controlled-NOT)",
        "purpose":   "Flips target qubit only when control qubit is |1⟩.",
        "intuition": "The entanglement engine. With a superposed control (use H first), "
                     "the target becomes correlated — this is a Bell state. "
                     "Measuring one qubit instantly determines the other.",
        "matrix":    "4×4: [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]",
        "actions":   "|00⟩→|00⟩  |01⟩→|01⟩  |10⟩→|11⟩  |11⟩→|10⟩",
        "uses":      "Bell states · teleportation · GHZ · error correction",
        "color":     "#34d399",
    },
}


def _gate_knowledge_panel(gate: str) -> None:
    info  = _GATE_KB[gate]
    color = info["color"]
    st.markdown(
        f'<div style="background:rgba(22,22,41,0.85); border:1px solid {color}44; '
        f'border-left:4px solid {color}; border-radius:8px; padding:14px 16px; margin-top:8px;">'
        f'<div style="display:flex; gap:10px; align-items:baseline; margin-bottom:6px;">'
        f'<span style="color:{color}; font-weight:700; font-size:1.1em; font-family:monospace;">{gate}</span>'
        f'<span style="color:#94a3b8; font-size:0.86em;">{info["full_name"]}</span>'
        f'</div>'
        f'<p style="color:#94a3b8; font-size:0.84em; margin:0 0 8px 0; line-height:1.5;">{info["intuition"]}</p>'
        f'<div style="display:flex; flex-wrap:wrap; gap:20px; font-size:0.82em; font-family:monospace;">'
        f'<span style="color:#475569;">Matrix: <span style="color:{color};">{info["matrix"]}</span></span>'
        f'<span style="color:#475569;">Action: <span style="color:#e2e8f0;">{info["actions"]}</span></span>'
        f'</div>'
        f'<div style="margin-top:8px; font-size:0.78em; color:#475569;">'
        f'Uses: {info["uses"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── State init ────────────────────────────────────────────────────────────────

def _init() -> None:
    defaults: dict = {
        "cp_gates":       [],
        "cp_results":     None,
        "cp_prev_qubits": 2,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Circuit builder ───────────────────────────────────────────────────────────

def _build_qc(n_qubits: int, gates: list) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, n_qubits)
    for g in gates:
        name = g["gate"]
        if name == "H":
            qc.h(g["qubit"])
        elif name == "X":
            qc.x(g["qubit"])
        elif name == "Y":
            qc.y(g["qubit"])
        elif name == "Z":
            qc.z(g["qubit"])
        elif name == "CNOT":
            qc.cx(g["control"], g["target"])
    qc.barrier()
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


# ── Gate-addition UI ──────────────────────────────────────────────────────────

def _gate_builder_row(n_qubits: int) -> None:
    st.markdown("#### Add Gate")
    col_gate, col_q1, col_q2, col_add = st.columns([2, 2, 2, 1], gap="small")

    with col_gate:
        gate = st.selectbox("Gate", ["H", "X", "Y", "Z", "CNOT"], key="cp_gate_sel")

    gate_info: dict = {"gate": gate}
    qubit_opts = list(range(n_qubits))
    fmt = lambda q: f"q{q}"  # noqa: E731

    if gate == "CNOT":
        with col_q1:
            ctrl = st.selectbox("Control", qubit_opts, key="cp_ctrl", format_func=fmt)
        with col_q2:
            tgt_opts = [q for q in qubit_opts if q != ctrl]
            if not tgt_opts:
                st.warning("Need ≥ 2 qubits for CNOT.")
                return
            tgt = st.selectbox("Target", tgt_opts, key="cp_tgt", format_func=fmt)
        gate_info["control"] = ctrl
        gate_info["target"]  = tgt
    else:
        with col_q1:
            qubit = st.selectbox("Qubit", qubit_opts, key="cp_qubit_sel", format_func=fmt)
        gate_info["qubit"] = qubit

    with col_add:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add ＋", type="primary", use_container_width=True):
            st.session_state.cp_gates.append(gate_info)
            st.session_state.cp_results = None

    _gate_knowledge_panel(gate)


# ── Gate sequence display ─────────────────────────────────────────────────────

def _gate_sequence_display(gates: list) -> None:
    if not gates:
        st.markdown(
            '<div style="color:#2d2d4e; text-align:center; padding:18px;">'
            'No gates yet — add them above.</div>',
            unsafe_allow_html=True,
        )
        return
    chips_html = ""
    for g in gates:
        if g["gate"] == "CNOT":
            label = f"CNOT&nbsp;q{g['control']}→q{g['target']}"
            css   = "gate-chip-cnot"
        else:
            label = f"{g['gate']}&nbsp;q{g['qubit']}"
            css   = "gate-chip"
        chips_html += f'<span class="{css}">{label}</span>'
    st.markdown(
        f'<div style="padding:10px 0; line-height:2.4;">{chips_html}</div>',
        unsafe_allow_html=True,
    )


# ── Result interpretation ─────────────────────────────────────────────────────

def _explain_results(gates: list, counts: dict, shots: int) -> str:
    gate_names = [g["gate"] for g in gates]
    has_h    = "H" in gate_names
    has_cnot = "CNOT" in gate_names
    n_states = len(counts)
    best     = max(counts, key=counts.get)
    p_best   = counts[best] / shots

    if has_h and has_cnot:
        return (
            f"H + CNOT can create **entangled Bell states** — {n_states} distinct outcomes observed, "
            f"|{best}⟩ most probable at p = {p_best:.3f}. Correlated qubit outcomes signal entanglement."
        )
    if has_h:
        return (
            f"Hadamard gates create **superposition** — roughly equal probability across states. "
            f"{n_states} distinct {len(best)}-qubit outcomes in {shots:,} shots."
        )
    if has_cnot:
        return (
            "CNOT in the computational basis (no H): deterministic flip of target when control=|1⟩. "
            "No superposition, no entanglement."
        )
    return (
        "Computational-basis gates only — near-deterministic output. "
        "Add an H gate first to see superposition effects."
    )


# ── Main render ───────────────────────────────────────────────────────────────

def render_circuit_playground() -> None:
    st.markdown("## ⚡ Quantum Circuit Playground")
    st.markdown(
        "*Gate-by-gate circuit builder backed by Qiskit Aer. "
        "Select any gate to see its unitary matrix, Bloch-sphere action, and typical use cases.*"
    )
    _init()

    # ── Configuration ─────────────────────────────────────────────────────────
    st.markdown("### Configuration")
    cfg_l, cfg_r = st.columns([2, 3], gap="large")

    with cfg_l:
        n_qubits = st.slider("Qubits", 1, 5, 2, key="cp_n_qubits")
        shots    = st.select_slider(
            "Simulation shots",
            options=[256, 512, 1024, 2048, 4096], value=1024,
        )
        st.caption(
            f"{n_qubits} qubit{'s' if n_qubits > 1 else ''} · "
            f"{2**n_qubits} possible outcomes · {shots:,} shots"
        )

    with cfg_r:
        _gate_builder_row(n_qubits)

    if st.session_state.cp_prev_qubits != n_qubits:
        st.session_state.cp_gates       = []
        st.session_state.cp_results     = None
        st.session_state.cp_prev_qubits = n_qubits

    st.divider()

    # ── Circuit sequence ──────────────────────────────────────────────────────
    st.markdown("### Current Circuit")
    _gate_sequence_display(st.session_state.cp_gates)

    act_l, act_m, act_r = st.columns([3, 1, 1])
    with act_l:
        run_disabled = len(st.session_state.cp_gates) == 0
        if st.button("▶  Run Simulation", type="primary",
                     disabled=run_disabled, use_container_width=True):
            with st.spinner("Running Qiskit Aer simulation…"):
                qc     = _build_qc(n_qubits, st.session_state.cp_gates)
                counts = run_circuit_simulation(qc, shots=shots)
            best_state = max(counts, key=counts.get)
            st.session_state.cp_results = {
                "counts":         counts,
                "shots":          shots,
                "n_qubits":       n_qubits,
                "circuit":        qc,
                "gates_snapshot": list(st.session_state.cp_gates),
            }
            log_experiment(
                exp_type="Circuit",
                label=f"{n_qubits}Q · " + " → ".join(
                    g["gate"] for g in st.session_state.cp_gates
                ),
                config={
                    "n_qubits": n_qubits,
                    "shots":    shots,
                    "gates":    list(st.session_state.cp_gates),
                },
                metrics={
                    "states_observed": len(counts),
                    "most_probable":   best_state,
                    "p_max":           round(counts[best_state] / shots, 4),
                    "shots":           shots,
                },
            )

    with act_m:
        if st.button("Remove last", use_container_width=True):
            if st.session_state.cp_gates:
                st.session_state.cp_gates.pop()
                st.session_state.cp_results = None
                st.rerun()

    with act_r:
        if st.button("Clear all", use_container_width=True):
            st.session_state.cp_gates   = []
            st.session_state.cp_results = None
            st.rerun()

    if run_disabled:
        st.caption("Add at least one gate, then click Run.")

    # ── Results ───────────────────────────────────────────────────────────────
    if not st.session_state.cp_results:
        return

    r        = st.session_state.cp_results
    counts   = r["counts"]
    shots_r  = r["shots"]
    qc       = r["circuit"]
    gates_ss = r["gates_snapshot"]

    st.divider()
    st.markdown("### Simulation Results")

    diag_col, summ_col = st.columns([3, 2], gap="large")

    with diag_col:
        st.markdown("**Circuit Diagram**")
        try:
            fig = qc.draw("mpl", fold=40)
            fig.patch.set_facecolor("#0D0D1A")
            for ax in fig.get_axes():
                ax.set_facecolor("#161629")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        except Exception:
            st.code(str(qc.draw("text")), language=None)

    with summ_col:
        st.markdown("**Measurement Summary**")
        best = max(counts, key=counts.get)
        p_best = counts[best] / shots_r
        st.metric("Unique States",     len(counts))
        st.metric("Most Probable",     f"|{best}⟩")
        st.metric("P(best state)",     f"{p_best:.4f}")
        st.metric("Shots",             f"{shots_r:,}")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**What happened**")
        st.markdown(_explain_results(gates_ss, counts, shots_r))

    chart_l, chart_r = st.columns(2, gap="small")
    with chart_l:
        st.plotly_chart(measurement_bar_chart(counts, shots_r), use_container_width=True)
    with chart_r:
        st.plotly_chart(probability_chart(counts, shots_r), use_container_width=True)

    with st.expander("Raw measurement data"):
        rows = [
            {
                "State":       f"|{k}⟩",
                "Count":       v,
                "Probability": round(v / shots_r, 6),
                "Percentage":  f"{v / shots_r * 100:.2f}%",
            }
            for k, v in sorted(counts.items(), key=lambda x: -x[1])
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

