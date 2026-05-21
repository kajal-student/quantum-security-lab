"""
Quantum Security & Behavior Visualization Lab
=============================================
Entry point. Run with:  streamlit run app.py
"""

from pathlib import Path
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Quantum Security & Behavior Visualization Lab",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject custom CSS ─────────────────────────────────────────────────────────
_css_path = Path(__file__).parent / "assets" / "styles.css"
if _css_path.exists():
    st.markdown(f"<style>{_css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:18px 0 20px 0;">
        <div style="font-size:1em; font-weight:600; color:#a78bfa; letter-spacing:0.01em;">
            ⚛️ Quantum Lab
        </div>
        <div style="font-size:0.75em; color:#475569; margin-top:3px;">
            Qiskit Aer · Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        options=[
            "Home",
            "Quantum Auth Lab",
            "Circuit Playground",
            "Randomness Analyzer",
            "Superposition Visualizer",
            "Noise Simulator",
            "Experiment Dashboard",
        ],
        label_visibility="collapsed",
    )

# ── Page routing (lazy imports keep startup fast) ─────────────────────────────
if page == "Home":
    from modules.home import render_home
    render_home()

elif page == "Quantum Auth Lab":
    from modules.auth_lab import render_auth_lab
    render_auth_lab()

elif page == "Circuit Playground":
    from modules.circuit_playground import render_circuit_playground
    render_circuit_playground()

elif page == "Randomness Analyzer":
    from modules.randomness_analyzer import render_randomness_analyzer
    render_randomness_analyzer()

elif page == "Superposition Visualizer":
    from modules.superposition_viz import render_superposition_viz
    render_superposition_viz()

elif page == "Noise Simulator":
    from modules.noise_simulator import render_noise_simulator
    render_noise_simulator()

elif page == "Experiment Dashboard":
    from modules.experiment_dashboard import render_experiment_dashboard
    render_experiment_dashboard()
