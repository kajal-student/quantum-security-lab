# ⚛️ Quantum Security & Behavior Visualization Lab

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Qiskit](https://img.shields.io/badge/Qiskit-1.x-6929C4?logo=ibm&logoColor=white)
![Qiskit Aer](https://img.shields.io/badge/Qiskit_Aer-0.14+-6929C4?logo=ibm&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E)

A full-stack quantum computing simulation platform built with **Qiskit Aer** and **Streamlit**. Six integrated modules cover quantum authentication, interactive circuit construction, noise modeling, state visualization, and session-wide experiment analytics with JSON/CSV export.

Every quantum operation runs on Qiskit's Aer local simulator — the same engine IBM Research uses for algorithm prototyping before hardware deployment. No IBM Quantum account required.

---

## Modules

| # | Module | What it demonstrates |
|---|--------|----------------------|
| 1 | 🔐 **Quantum Auth Lab** | 32-qubit Hadamard token generation, Shannon entropy, session management |
| 2 | ⚡ **Circuit Playground** | Gate-by-gate circuit builder (H, X, Y, Z, CNOT), up to 4096-shot Aer simulation, per-gate knowledge panel |
| 3 | 🎲 **Randomness Analyzer** | NumPy PRNG vs Qiskit quantum RNG — distribution comparison, entropy, sequential independence |
| 4 | 🌀 **Superposition Visualizer** | 2D Bloch sphere cross-section, gate transforms, Born-rule measurement simulation, full gate reference |
| 5 | 🔧 **Noise Simulator** | Depolarizing / bit-flip / phase-flip noise on Bell & GHZ states, Total Variation Distance gauge |
| 6 | 📊 **Experiment Dashboard** | Session-wide log, per-module rerun, summary analytics, JSON + CSV export |

---

## Project Structure

```
quantum_lab/
├── app.py                          # Entry point — Streamlit routing (7 pages)
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Dark theme (#0D0D1A background, #7C3AED accent)
├── assets/
│   └── styles.css                  # Shared CSS — cards, token-box, gate-chips, badges
├── auth/
│   └── quantum_auth.py             # Token gen, circuit simulation, preset circuits, noise model builder
├── modules/
│   ├── home.py                     # Landing page with 6-module grid and architecture diagram
│   ├── auth_lab.py                 # Quantum Auth Lab UI
│   ├── circuit_playground.py       # Circuit Playground UI and gate knowledge panel
│   ├── randomness_analyzer.py      # Classical vs quantum randomness comparison
│   ├── superposition_viz.py        # Bloch sphere, measurement simulation, gate reference
│   ├── noise_simulator.py          # Noise model comparison with TVD metric
│   └── experiment_dashboard.py     # Experiment log, analytics, rerun, export
├── visualizations/
│   └── charts.py                   # All Plotly chart functions (12 total, shared palette)
└── utils/
    └── helpers.py                  # Entropy, Bloch math, TVD, session experiment log
```

---

## Setup

### Prerequisites
- Python 3.10 or later
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-handle>/quantum-security-lab.git
cd quantum-security-lab/quantum_lab

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

> **First run is slower** — Qiskit compiles circuits on first execution. Subsequent runs are fast.

---

## Dependencies

```
streamlit>=1.32.0      # Web UI and session state
qiskit>=1.1.0          # Quantum circuit construction
qiskit-aer>=0.14.0     # Local quantum simulator and noise models
plotly>=5.20.0         # Interactive dark-themed charts
matplotlib>=3.8.0      # Circuit diagram rendering (mpl backend)
numpy>=1.26.0          # Numerical arrays and PRNG
pandas>=2.1.0          # Tabular data display (DataFrames)
pylatexenc>=2.10       # LaTeX gate labels in Matplotlib circuit diagrams
pillow>=10.1.0         # Image support for Matplotlib figure export
```

All dependencies are standard Python packages. No cloud accounts, API keys, or hardware access required.

---

## Key Technical Decisions

**`AerSimulator.run(qc, shots=n)` — not `transpile(qc, backend)`.**
Calling `transpile` with a simulator backend triggers coupling-map validation, capping circuits at 28 qubits and breaking 32-qubit token generation. `AerSimulator` accepts circuits directly without topology constraints.

**2D Bloch sphere cross-section.**
A full 3D Bloch sphere in Plotly requires complex surface math and renders poorly against dark backgrounds. The xz-plane projection is exact for real-amplitude states (all Pauli + H gates applied to |0⟩ / |1⟩) and communicates the same intuition with cleaner visuals.

**Total Variation Distance as the noise metric.**
TVD = 0.5 × Σ|p\_clean − p\_noisy| maps to [0, 1.0]. It is computed directly from measurement counts — no statevector access needed — and is interpretable: 0 means noise had no statistical effect; 1.0 means the distributions share no probability mass.

**Session-state experiment log.**
All six modules call a shared `log_experiment()` helper that appends a typed dict to `st.session_state["exp_log"]` (capped at 30 entries). The Dashboard reads the same list — no database required for a single-session demo.

**Noise model per call.**
`run_noisy_circuit` creates a fresh `AerSimulator(noise_model=nm)` on each invocation rather than mutating a shared simulator. This avoids cross-experiment state bleed when users change noise parameters between runs.

---

## Quantum Concepts Covered

| Concept | Where it appears |
|---------|-----------------|
| Hadamard superposition | Auth Lab token circuit, Superposition Visualizer |
| Born rule: P(|0⟩) = cos²(θ/2) | Superposition Visualizer — Measurement tab |
| Bloch sphere geometry | Superposition Visualizer — State Explorer |
| Quantum entanglement (Bell / GHZ states) | Noise Simulator preset circuits, Circuit Playground |
| NISQ noise models | Noise Simulator (depolarizing, bit-flip, phase-flip) |
| Total Variation Distance | Noise Simulator TVD gauge |
| Shannon entropy | Auth Lab, Randomness Analyzer |
| Quantum vs classical randomness | Randomness Analyzer |
| Gate unitarity and matrix representation | Circuit Playground knowledge panel, Gate Reference |

---

## Resume Section

**Quantum Security & Behavior Visualization Lab** — Python · Qiskit 1.x · Qiskit Aer · Streamlit · Plotly

- Built a 6-module quantum simulation platform (Qiskit Aer + Streamlit) spanning authentication, circuit construction, noise modeling, and state visualization, shipped as a runnable web app with dark-theme Plotly analytics and session-wide experiment logging with JSON/CSV export.

- Implemented three NISQ-era noise models (depolarizing, bit-flip, phase-flip) using Qiskit Aer's `NoiseModel` API; quantified decoherence on Bell and GHZ states via Total Variation Distance, surfaced as an interactive color-coded gauge.

- Designed a 32-qubit quantum authentication system — Hadamard superposition circuits generating quantum-random session tokens — with real-time Shannon entropy visualization and per-token qubit-state distribution charts.

- Engineered a cross-module experiment logging system aggregating Token, Circuit, Noise, and Randomness runs into a unified dashboard with one-click rerun into source modules and date-stamped JSON/CSV export.

---

## How to Explain This in an Interview

**"Walk me through the project."**

> "It's a quantum computing lab I built to demonstrate practical quantum applications end to end, using Qiskit Aer as the simulation backend and Streamlit as the web UI.
>
> The core engineering challenge I hit early was the Qiskit 1.x API: calling `transpile(circuit, simulator)` triggers coupling-map validation and silently caps circuits at 28 qubits, which broke my 32-qubit token generator. The fix was to call `AerSimulator.run(circuit, shots=n)` directly — which is actually the correct pattern for simulators.
>
> For the noise simulator, I built three noise models — depolarizing, bit-flip, and phase-flip — using `qiskit_aer.noise.NoiseModel`. I chose Total Variation Distance as the quality metric because it's computable purely from measurement count histograms, maps cleanly to [0, 0.5], and is intuitive to explain: 0 means noise had no measurable effect, 0.5 means the distributions are completely uncorrelated.
>
> For the Bloch sphere, I chose a 2D xz-plane cross-section instead of a 3D surface. All the standard gates — H, X, Y, Z — operate on real-amplitude states that lie in that plane, so the math is exact. H|0⟩ lands at |+⟩ (x=1, z=0), X|0⟩ lands at |1⟩ (z=−1), Z|+⟩ flips to |−⟩ (x=−1). It's far more readable than a 3D Plotly surface on a dark background.
>
> The experiment dashboard is what ties it all together. Every module calls a shared `log_experiment()` that appends typed records to Streamlit session state. The dashboard reads, filters, reruns experiments back into their source modules, and exports everything as JSON or CSV. That design — a central log decoupled from individual modules — is the kind of thinking that applies to any data pipeline."

**Expected follow-up: "What's the difference between statevector and QASM simulation?"**
> Statevector gives you exact quantum amplitudes — exponential memory, but precise. QASM samples from the probability distribution a fixed number of times (shots), giving you realistic count histograms. Aer supports both; I use QASM (shots-based) throughout this lab to mimic what real hardware actually returns.

**Expected follow-up: "Could this run on real quantum hardware?"**
> Yes. The only change is swapping `AerSimulator` for an `IBMQBackend` from `qiskit_ibm_runtime`. The circuit construction code doesn't change at all — that's the whole point of Qiskit's abstraction layer.

---

## License

MIT
