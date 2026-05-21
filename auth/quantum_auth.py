"""
Quantum token generation, circuit simulation, and noise modelling using Qiskit Aer.

All operations run on a local AerSimulator — statistically equivalent to real
quantum hardware but fully offline.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error  # type: ignore[import-untyped]

from utils.helpers import format_token_hex, bitstring_entropy

# Shared clean simulator — no coupling-map limits, accepts circuits directly
_SIM = AerSimulator()


# ── Token generation ──────────────────────────────────────────────────────────

def generate_quantum_token(n_qubits: int = 32) -> dict:
    """
    Generate a quantum-random session token via Hadamard + measurement.

    Returns a dict with bitstring, token_hex, entropy, qubit counts,
    and a display_circuit (8 qubits) for diagram rendering.
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    for i in range(n_qubits):
        qc.h(i)
    qc.barrier()
    qc.measure(range(n_qubits), range(n_qubits))

    result    = _SIM.run(qc, shots=1).result()
    bitstring = list(result.get_counts().keys())[0].replace(" ", "")

    display_n = min(8, n_qubits)
    disp_qc   = QuantumCircuit(display_n, display_n)
    for i in range(display_n):
        disp_qc.h(i)
    disp_qc.barrier()
    disp_qc.measure(range(display_n), range(display_n))

    return {
        "bitstring":       bitstring,
        "token_hex":       format_token_hex(bitstring),
        "n_qubits":        n_qubits,
        "entropy":         bitstring_entropy(bitstring),
        "ones_count":      bitstring.count("1"),
        "zeros_count":     bitstring.count("0"),
        "display_circuit": disp_qc,
    }


# ── Clean circuit simulation ──────────────────────────────────────────────────

def run_circuit_simulation(qc: QuantumCircuit, shots: int = 1024) -> dict:
    """Run a QuantumCircuit on AerSimulator; return sorted measurement counts."""
    result = _SIM.run(qc, shots=shots).result()
    counts = result.get_counts()
    return {k.replace(" ", ""): v for k, v in sorted(counts.items())}


# ── Quantum random samples ────────────────────────────────────────────────────

def generate_quantum_random_samples(n_samples: int, bits_per_sample: int = 8) -> np.ndarray:
    """
    Return n_samples quantum-random integers in [0, 2**bits_per_sample).

    Each sample is derived from collapsing bits_per_sample qubits that were
    placed in equal superposition by Hadamard gates.
    """
    qc = QuantumCircuit(bits_per_sample, bits_per_sample)
    for i in range(bits_per_sample):
        qc.h(i)
    qc.measure(range(bits_per_sample), range(bits_per_sample))

    result = _SIM.run(qc, shots=n_samples).result()
    counts = result.get_counts()

    samples: list[int] = []
    for bitstring, count in counts.items():
        val = int(bitstring.replace(" ", ""), 2)
        samples.extend([val] * count)

    rng = np.random.default_rng()
    arr = np.array(samples[:n_samples], dtype=np.int64)
    rng.shuffle(arr)
    return arr


# ── Preset circuits for noise simulation ─────────────────────────────────────

PRESET_CIRCUITS: dict[str, int] = {
    "Superposition (H)": 1,
    "Bell State":        2,
    "GHZ State":         3,
    "Bit Flip (X)":      1,
}


def build_preset_circuit(name: str) -> QuantumCircuit:
    """Return a ready-to-run QuantumCircuit for the named preset."""
    if name == "Superposition (H)":
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)

    elif name == "Bell State":
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])

    elif name == "GHZ State":
        qc = QuantumCircuit(3, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure([0, 1, 2], [0, 1, 2])

    elif name == "Bit Flip (X)":
        qc = QuantumCircuit(1, 1)
        qc.x(0)
        qc.measure(0, 0)

    else:
        raise ValueError(f"Unknown preset circuit: '{name}'")

    return qc


# ── Noisy simulation ──────────────────────────────────────────────────────────

def run_noisy_circuit(
    qc: QuantumCircuit,
    noise_type: str,
    noise_level: float,
    shots: int = 1024,
) -> dict:
    """
    Run qc under a specified noise model and return sorted measurement counts.

    noise_type: "Depolarizing" | "Bit Flip" | "Phase Flip"
    noise_level: error probability per gate (0.0 – 0.25 recommended)
    """
    nm = _build_noise_model(noise_type, noise_level)
    noisy_sim = AerSimulator(noise_model=nm)
    result    = noisy_sim.run(qc, shots=shots).result()
    counts    = result.get_counts()
    return {k.replace(" ", ""): v for k, v in sorted(counts.items())}


def _build_noise_model(noise_type: str, p: float) -> NoiseModel:
    nm = NoiseModel()
    p  = max(0.0, min(p, 1.0))

    if noise_type == "Depolarizing":
        e1q = depolarizing_error(p, 1)
        e2q = depolarizing_error(min(p * 1.5, 1.0), 2)
        nm.add_all_qubit_quantum_error(e1q, ["h", "x", "y", "z"])
        nm.add_all_qubit_quantum_error(e2q, ["cx"])
        nm.add_all_qubit_quantum_error(depolarizing_error(p / 2, 1), ["measure"])

    elif noise_type == "Bit Flip":
        err = pauli_error([("X", p), ("I", 1.0 - p)])
        nm.add_all_qubit_quantum_error(err, ["h", "x", "y", "z", "measure"])

    elif noise_type == "Phase Flip":
        err = pauli_error([("Z", p), ("I", 1.0 - p)])
        nm.add_all_qubit_quantum_error(err, ["h", "x", "y", "z", "measure"])

    return nm
