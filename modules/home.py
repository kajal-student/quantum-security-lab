import streamlit as st

# Shared card style used for all 6 module cards
_CARD = (
    "background:rgba(22,22,41,0.55); border:1px solid rgba(255,255,255,0.06); "
    "border-radius:10px; padding:20px 22px; border-left:3px solid {color};"
)


def render_home() -> None:
    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:36px 0 24px 0;">
        <h1 style="font-size:2em; color:#a78bfa; margin:0 0 8px 0; letter-spacing:-0.3px;">
            Quantum Security &amp; Behavior Visualization Lab
        </h1>
        <p style="font-size:0.95em; color:#64748b; max-width:680px; line-height:1.65; margin:0;">
            Six integrated modules for exploring quantum circuits, authentication,
            noise modeling, and state visualization — all backed by Qiskit's Aer
            local simulator. Session runs are logged and exportable as JSON or CSV.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Module grid ───────────────────────────────────────────────────────────
    st.markdown("### Modules")

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(
            f'<div style="{_CARD.format(color="#7C3AED")}">'
            f'<div style="font-weight:600; color:#a78bfa; margin-bottom:6px;">Quantum Auth Lab</div>'
            f'<p style="color:#64748b; font-size:0.85em; line-height:1.55; margin:0;">'
            f'32-qubit Hadamard circuit generates a quantum-random session token. '
            f'Token entropy, qubit state distribution, and session validity are visualised in real time.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f'<div style="{_CARD.format(color="#10b981")}">'
            f'<div style="font-weight:600; color:#34d399; margin-bottom:6px;">Circuit Playground</div>'
            f'<p style="color:#64748b; font-size:0.85em; line-height:1.55; margin:0;">'
            f'Gate-by-gate circuit builder (H, X, Y, Z, CNOT) with up to 4096-shot Aer simulation. '
            f'Each gate shows its unitary matrix, Bloch-sphere action, and typical use cases.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f'<div style="{_CARD.format(color="#f59e0b")}">'
            f'<div style="font-weight:600; color:#fbbf24; margin-bottom:6px;">Randomness Analyzer</div>'
            f'<p style="color:#64748b; font-size:0.85em; line-height:1.55; margin:0;">'
            f'Compares NumPy\'s Mersenne Twister PRNG against Hadamard-circuit quantum samples. '
            f'Shannon entropy, distribution histograms, and sequential independence metrics.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3, gap="medium")

    with col4:
        st.markdown(
            f'<div style="{_CARD.format(color="#38bdf8")}">'
            f'<div style="font-weight:600; color:#7dd3fc; margin-bottom:6px;">Superposition Visualizer</div>'
            f'<p style="color:#64748b; font-size:0.85em; line-height:1.55; margin:0;">'
            f'2D Bloch-sphere cross-section showing gate transforms on named states. '
            f'Measurement simulation verifies Born-rule probabilities. Gate reference with full matrices.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            f'<div style="{_CARD.format(color="#ef4444")}">'
            f'<div style="font-weight:600; color:#f87171; margin-bottom:6px;">Noise Simulator</div>'
            f'<p style="color:#64748b; font-size:0.85em; line-height:1.55; margin:0;">'
            f'Applies depolarizing, bit-flip, or phase-flip noise to preset circuits '
            f'(Bell, GHZ). Total Variation Distance quantifies the degradation.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

    with col6:
        st.markdown(
            f'<div style="{_CARD.format(color="#a78bfa")}">'
            f'<div style="font-weight:600; color:#c4b5fd; margin-bottom:6px;">Experiment Dashboard</div>'
            f'<p style="color:#64748b; font-size:0.85em; line-height:1.55; margin:0;">'
            f'Aggregates all session runs across modules. Per-experiment rerun, '
            f'summary analytics, and JSON/CSV export.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Architecture ──────────────────────────────────────────────────────────
    st.markdown("### Architecture")
    arch_col, stack_col = st.columns([3, 2], gap="large")

    with arch_col:
        st.markdown("""
        <div class="arch-box">
<pre style="margin:0; line-height:1.7; font-size:0.81em;">
┌─────────────────────────────────────────────────────────────┐
│                 Streamlit frontend (app.py)                  │
│  Auth  │  Circuit  │  Randomness  │  Superpositon  │  Noise  │  Dashboard
└────────┴─────┬─────┴──────────────┴────────────────┴─────────┘
               │  all modules import from:
┌──────────────▼───────────────────────────────────────────────┐
│  auth/quantum_auth.py   visualizations/charts.py             │
│  utils/helpers.py       assets/styles.css                    │
└──────────────┬───────────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────────┐
│              Qiskit Aer (AerSimulator)                       │
│  clean simulation  ·  noise models  ·  statevector           │
└──────────────────────────────────────────────────────────────┘</pre>
        </div>
        """, unsafe_allow_html=True)

    with stack_col:
        st.markdown("**Stack**")
        stack = [
            ("Qiskit 1.x",    "Circuit construction and gate model",  "#7C3AED"),
            ("Qiskit Aer",    "Local simulator and noise models",      "#a78bfa"),
            ("Streamlit",     "Web UI and session state",              "#38bdf8"),
            ("Plotly",        "Interactive charts",                    "#10b981"),
            ("Matplotlib",    "Circuit diagram rendering",             "#f59e0b"),
            ("Python 3.10+",  "Application layer",                    "#64748b"),
        ]
        for name, desc, color in stack:
            st.markdown(
                f'<div style="display:flex; align-items:baseline; margin:7px 0; '
                f'padding:8px 12px; background:rgba(22,22,41,0.5); '
                f'border-radius:6px; border-left:2px solid {color};">'
                f'<span style="color:{color}; font-weight:600; min-width:110px; '
                f'font-size:0.84em; font-family:monospace;">{name}</span>'
                f'<span style="color:#475569; font-size:0.81em;">{desc}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Background ────────────────────────────────────────────────────────────
    st.markdown("### Background")
    p1, p2 = st.columns(2, gap="large")

    with p1:
        st.markdown("""
        **Quantum randomness**

        Classical PRNGs (Mersenne Twister, ChaCha20) are deterministic — given the
        internal state, the full output sequence is reproducible. Quantum measurement
        is physically non-deterministic: a qubit in |+⟩ = (|0⟩ + |1⟩)/√2 collapses
        to 0 or 1 with exactly 50% probability, with the outcome undecided until the
        moment of measurement.

        **Noise in quantum hardware**

        Current NISQ devices achieve ~99–99.9% gate fidelity. A 100-gate circuit
        accumulates meaningful error. Total Variation Distance provides a
        distribution-level metric for quantifying this degradation without requiring
        access to statevectors.
        """)

    with p2:
        st.markdown("""
        **Simulation vs hardware**

        All circuits run on Qiskit's Aer local simulator. The probability distributions,
        noise model behaviour, and Bloch-sphere transforms are mathematically correct —
        the only difference from real hardware is that the randomness is
        pseudo-random rather than physically undetermined.

        **What the simulator does not model:** qubit crosstalk, readout errors,
        T1/T2 decoherence, or device-specific gate calibration. These would appear on
        real hardware and are why error mitigation is an active research area.
        """)

    # ── Getting started ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-block">
        Use the sidebar to navigate. A natural flow: <em>Auth Lab</em> → generate a token →
        <em>Circuit Playground</em> → build a Bell state → <em>Noise Simulator</em> →
        observe decoherence → <em>Experiment Dashboard</em> → export results.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="q-footer">Quantum Security &amp; Behavior Visualization Lab · '
        'Qiskit · Streamlit · Plotly</div>',
        unsafe_allow_html=True,
    )
