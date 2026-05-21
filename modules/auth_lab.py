"""
Quantum Authentication Lab
==========================
Signup / login flow backed by a 32-qubit Hadamard token circuit.
Demonstrates quantum randomness, Shannon entropy, and session management.
"""

import time
import matplotlib
import matplotlib.pyplot as plt
import streamlit as st

from auth.quantum_auth import generate_quantum_token
from visualizations.charts import (
    entropy_gauge,
    session_validity_gauge,
    token_bit_distribution,
)
from utils.helpers import hash_password, time_remaining, token_expiry_ts, log_experiment

matplotlib.use("Agg")

# ── Session-state initialisation ──────────────────────────────────────────────

def _init() -> None:
    defaults = {
        "qa_users": {},       # username → {password_hash, created_at}
        "qa_session": None,   # active session dict or None
        "qa_view": "login",   # "login" | "signup"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Login panel ───────────────────────────────────────────────────────────────

def _login_panel() -> None:
    st.markdown("#### Login to your account")
    username = st.text_input("Username", key="qa_login_user", placeholder="your_username")
    password = st.text_input("Password", key="qa_login_pass", type="password", placeholder="••••••••")

    if st.button("Login — generate quantum session", type="primary", use_container_width=True):
        if not username or not password:
            st.error("Both fields are required.")
            return

        users = st.session_state.qa_users
        if username not in users:
            st.error("User not found. Please sign up first.")
            return
        if users[username]["password_hash"] != hash_password(password):
            st.error("Incorrect password.")
            return

        with st.spinner("Generating 32-qubit quantum session token…"):
            token_data = generate_quantum_token(n_qubits=32)

        st.session_state.qa_session = {
            "username": username,
            "token": token_data,
            "created_at": time.time(),
            "expires_at": token_expiry_ts(minutes=30),
        }
        log_experiment(
            exp_type="Token",
            label=f"32Q token · {username}",
            config={"n_qubits": 32, "username": username},
            metrics={
                "entropy":    round(token_data["entropy"], 4),
                "ones_ratio": round(token_data["ones_count"] / 32, 4),
            },
        )
        st.rerun()


# ── Signup panel ──────────────────────────────────────────────────────────────

def _signup_panel() -> None:
    st.markdown("#### Create a new account")
    username = st.text_input("Username", key="qa_su_user", placeholder="quantum_user_42")
    password = st.text_input("Password (min 6 chars)", key="qa_su_pass", type="password")
    confirm  = st.text_input("Confirm password", key="qa_su_confirm", type="password")

    if st.button("Create account", type="primary", use_container_width=True):
        if not username or not password:
            st.error("All fields are required.")
            return
        if len(password) < 6:
            st.error("Password must be at least 6 characters.")
            return
        if password != confirm:
            st.error("Passwords do not match.")
            return
        if username in st.session_state.qa_users:
            st.error("Username already taken.")
            return

        st.session_state.qa_users[username] = {
            "password_hash": hash_password(password),
            "created_at": time.time(),
        }
        st.toast(f"Account '{username}' created. Switch to the Login tab.", icon="✅")
        st.rerun()


# ── Session dashboard ─────────────────────────────────────────────────────────

def _session_dashboard(session: dict) -> None:
    token = session["token"]
    remaining = time_remaining(session["expires_at"])

    if remaining["expired"]:
        st.error("Session expired. Please log in again.")
        st.session_state.qa_session = None
        st.rerun()
        return

    # Header row
    hdr_l, hdr_r = st.columns([4, 1])
    with hdr_l:
        st.markdown(
            f"### Active session — `{session['username']}`&nbsp;&nbsp;"
            f'<span class="badge-active">● AUTHENTICATED</span>',
            unsafe_allow_html=True,
        )
    with hdr_r:
        if st.button("Logout", use_container_width=True):
            st.session_state.qa_session = None
            st.rerun()

    st.divider()

    # ── Token display ─────────────────────────────────────────────────────────
    st.markdown("#### Quantum Session Token")

    tok_l, tok_r = st.columns([3, 2], gap="large")

    with tok_l:
        st.markdown("**Hex Token (32-bit)**")
        # Format hex in groups of 4 for readability
        raw_hex = token["token_hex"]
        grouped = " ".join(raw_hex[i:i+4] for i in range(0, len(raw_hex), 4))
        st.markdown(f'<div class="token-box">{grouped}</div>', unsafe_allow_html=True)

        st.markdown("<br>**Binary Bitstring**", unsafe_allow_html=True)
        bs = token["bitstring"]
        # Show full 32-bit string in two 16-char lines
        grouped_bin = " ".join(bs[i:i+4] for i in range(0, len(bs), 4))
        st.markdown(f'<div class="token-box" style="font-size:11px;">{grouped_bin}</div>',
                    unsafe_allow_html=True)

    with tok_r:
        st.markdown("**Token Statistics**")
        c1, c2 = st.columns(2)
        c1.metric("Total Qubits", token["n_qubits"])
        c2.metric("Bit Entropy", f"{token['entropy']:.4f}")
        c1.metric("|1⟩ Count", token["ones_count"])
        c2.metric("|0⟩ Count", token["zeros_count"])
        st.caption(
            "Entropy of 1.0 bits/symbol = perfect 50/50 split between "
            "|0⟩ and |1⟩ outcomes — maximum per-bit randomness."
        )

    st.divider()

    # ── Visual metrics row ────────────────────────────────────────────────────
    st.markdown("#### Token Analytics")
    viz1, viz2, viz3 = st.columns(3, gap="small")

    with viz1:
        st.plotly_chart(token_bit_distribution(token["bitstring"]), use_container_width=True)
    with viz2:
        st.plotly_chart(
            entropy_gauge(token["entropy"], max_entropy=1.0, title="Bit Entropy"),
            use_container_width=True,
        )
    with viz3:
        st.plotly_chart(
            session_validity_gauge(
                min(1.0, remaining["fraction"]),
                remaining["minutes"],
                remaining["seconds"],
            ),
            use_container_width=True,
        )

    st.info(
        f"Session expires in **{remaining['minutes']}m {remaining['seconds']}s**. "
        "Tokens are single-use per session and regenerated on each login."
    )

    st.divider()

    # ── Circuit diagram ───────────────────────────────────────────────────────
    st.markdown("#### Token Generation Circuit (8-qubit display)")
    st.caption(
        "The full 32-qubit circuit uses the same pattern — one Hadamard per qubit "
        "creates superposition, measurement collapses each to a random classical bit."
    )

    with st.spinner("Rendering circuit diagram…"):
        try:
            fig = token["display_circuit"].draw("mpl", fold=-1)
            fig.patch.set_facecolor("#0D0D1A")
            for ax in fig.get_axes():
                ax.set_facecolor("#161629")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        except Exception as exc:
            st.warning(f"Matplotlib rendering unavailable: {exc}")
            st.code(str(token["display_circuit"].draw("text")), language=None)

    st.divider()

    # ── Educational expander ──────────────────────────────────────────────────
    with st.expander("How quantum session tokens work"):
        st.markdown("""
**Generation pipeline**

1. A `QuantumCircuit(32, 32)` is constructed in Qiskit.
2. A **Hadamard gate** `H` is applied to each of the 32 qubits, placing them all in
   equal superposition: |+⟩ = (|0⟩ + |1⟩) / √2.
3. All qubits are **measured** simultaneously. Quantum measurement collapses each
   superposition to a definite |0⟩ or |1⟩ with 50% probability — independent of
   every other qubit.
4. The 32-bit measurement outcome is the token bitstring, converted to 8 hex chars.

**Security properties**

| Property | Classical PRNG | Quantum (this lab) |
|---|---|---|
| Seed dependency | Yes — predictable with seed | No — no deterministic seed |
| Reproducibility | Yes, given seed | No, physically impossible |
| Statistical quality | Excellent | Excellent |
| Source of randomness | Algorithm | Quantum measurement |

*This lab simulates quantum behaviour classically using Qiskit Aer. On real quantum
hardware (IBM Quantum, IonQ), the randomness would be certified by NIST SP 800-90B.*
        """)


# ── Main render ───────────────────────────────────────────────────────────────

def render_auth_lab() -> None:
    st.markdown("## 🔐 Quantum Authentication Lab")
    st.markdown(
        "*Quantum-random session tokens generated via Hadamard superposition circuits.*"
    )
    _init()

    if st.session_state.qa_session:
        _session_dashboard(st.session_state.qa_session)
        return

    # ── Auth tabs ─────────────────────────────────────────────────────────────
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        _login_panel()

    with tab_signup:
        _signup_panel()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-block">
        💡 <strong>Demo flow:</strong> open the <em>Sign Up</em> tab, create an account,
        then log in to generate your quantum session token and explore the analytics.
    </div>
    """, unsafe_allow_html=True)
