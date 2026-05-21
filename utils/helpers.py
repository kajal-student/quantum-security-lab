import math
import hashlib
import time
import numpy as np


# ── Entropy ──────────────────────────────────────────────────────────────────

def calculate_shannon_entropy(data: np.ndarray) -> float:
    """Shannon entropy (bits) over the value distribution of an integer array."""
    arr = np.asarray(data).flatten()
    if arr.size == 0:
        return 0.0
    _, counts = np.unique(arr, return_counts=True)
    probs = counts / arr.size
    return float(-np.sum(probs * np.log2(probs + 1e-15)))


def bitstring_entropy(bitstring: str) -> float:
    """Per-symbol Shannon entropy of a binary string (max = 1.0 at 50/50 split)."""
    n = len(bitstring)
    if n == 0:
        return 0.0
    p1 = bitstring.count("1") / n
    p0 = 1.0 - p1
    h = 0.0
    if p0 > 0:
        h -= p0 * math.log2(p0)
    if p1 > 0:
        h -= p1 * math.log2(p1)
    return h


# ── Auth helpers ──────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def format_token_hex(bitstring: str) -> str:
    bitstring = bitstring.replace(" ", "")
    if not bitstring:
        return ""
    int_val = int(bitstring, 2)
    n_hex = max(1, len(bitstring) // 4)
    return hex(int_val)[2:].upper().zfill(n_hex)


def token_expiry_ts(minutes: int = 30) -> float:
    return time.time() + minutes * 60


def time_remaining(expiry_ts: float, total_minutes: int = 30) -> dict:
    remaining = max(0.0, expiry_ts - time.time())
    total = total_minutes * 60
    return {
        "total_seconds": remaining,
        "minutes": int(remaining // 60),
        "seconds": int(remaining % 60),
        "expired": remaining <= 0,
        "fraction": remaining / total,
    }


# ── Stats helpers ─────────────────────────────────────────────────────────────

def runs_change_ratio(data: np.ndarray) -> float:
    """Fraction of consecutive pairs with different values — independence proxy."""
    if len(data) < 2:
        return 0.0
    return float(np.sum(np.diff(data) != 0) / (len(data) - 1))


# ── Bloch sphere math ─────────────────────────────────────────────────────────

# Named single-qubit states → (x, y, z) Bloch coordinates
_STATE_BLOCH: dict[str, tuple[float, float, float]] = {
    "|0⟩":  ( 0.0,  0.0,  1.0),
    "|1⟩":  ( 0.0,  0.0, -1.0),
    "|+⟩":  ( 1.0,  0.0,  0.0),
    "|−⟩":  (-1.0,  0.0,  0.0),
    "|i⟩":  ( 0.0,  1.0,  0.0),
    "|−i⟩": ( 0.0, -1.0,  0.0),
}


def state_to_bloch(name: str) -> tuple[float, float, float]:
    return _STATE_BLOCH.get(name, (0.0, 0.0, 1.0))


def bloch_from_angles(theta: float, phi: float) -> tuple[float, float, float]:
    """Convert spherical Bloch angles (theta, phi) to Cartesian (x, y, z)."""
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    return x, y, z


def apply_gate_bloch(gate: str, x: float, y: float, z: float) -> tuple[float, float, float]:
    """
    Apply a single-qubit gate as a rotation on the Bloch sphere.

    All Pauli gates and H are π-rotations around their respective axes:
      X: π around X-axis  → (x, -y, -z)
      Y: π around Y-axis  → (-x, y, -z)
      Z: π around Z-axis  → (-x, -y, z)
      H: π around (X+Z)/√2 axis → (z, -y, x)   [swaps x and z]
    """
    if gate == "H":
        return z, -y, x
    if gate == "X":
        return x, -y, -z
    if gate == "Y":
        return -x, y, -z
    if gate == "Z":
        return -x, -y, z
    return x, y, z


def bloch_to_probs(z: float) -> tuple[float, float]:
    """Return (P(|0⟩), P(|1⟩)) from the z-component of a Bloch vector."""
    p0 = (1.0 + z) / 2.0
    p1 = (1.0 - z) / 2.0
    return p0, p1


# ── Quantum distance metrics ──────────────────────────────────────────────────

def tvd(counts_a: dict, counts_b: dict, shots: int) -> float:
    """
    Total Variation Distance between two measurement count distributions.
    Formula: 0.5 * Σ |p_a(s) - p_b(s)| over all observed states s.
    Range [0, 1]: 0 = identical distributions, 1 = completely disjoint support.
    """
    all_states = set(counts_a) | set(counts_b)
    return 0.5 * sum(
        abs(counts_a.get(s, 0) / shots - counts_b.get(s, 0) / shots)
        for s in all_states
    )


# ── Experiment logging ────────────────────────────────────────────────────────

_LOG_KEY = "exp_log"
_ID_KEY  = "exp_id_counter"
_MAX_EXPERIMENTS = 30


def log_experiment(exp_type: str, label: str, config: dict, metrics: dict) -> None:
    """Append an experiment record to the session-state log."""
    import streamlit as st
    if _LOG_KEY not in st.session_state:
        st.session_state[_LOG_KEY] = []
    if _ID_KEY not in st.session_state:
        st.session_state[_ID_KEY] = 0

    st.session_state[_ID_KEY] += 1
    entry = {
        "id": st.session_state[_ID_KEY],
        "timestamp": time.time(),
        "type": exp_type,
        "label": label,
        "config": config,
        "metrics": metrics,
    }
    st.session_state[_LOG_KEY].insert(0, entry)          # newest first
    st.session_state[_LOG_KEY] = st.session_state[_LOG_KEY][:_MAX_EXPERIMENTS]


def get_experiment_log() -> list:
    import streamlit as st
    return st.session_state.get(_LOG_KEY, [])


def clear_experiment_log() -> None:
    import streamlit as st
    st.session_state[_LOG_KEY] = []
    st.session_state[_ID_KEY]  = 0
