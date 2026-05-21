"""
Reusable Plotly chart components for the Quantum Security & Behavior Visualization Lab.
All charts share a consistent dark colour palette defined in C.
"""

import numpy as np
import plotly.graph_objects as go

# ── Shared palette ────────────────────────────────────────────────────────────
C = {
    "bg":        "#0D0D1A",
    "card":      "#161629",
    "grid":      "#1e1e3a",
    "text":      "#E2E8F0",
    "muted":     "#64748b",
    "primary":   "#7C3AED",
    "secondary": "#a78bfa",
    "accent":    "#10b981",
    "amber":     "#f59e0b",
    "danger":    "#ef4444",
    "cyan":      "#38bdf8",
}

_BASE_LAYOUT = dict(
    paper_bgcolor=C["bg"],
    plot_bgcolor=C["card"],
    font=dict(color=C["text"], family="monospace"),
    margin=dict(l=48, r=24, t=48, b=40),
)


def _axis(gridcolor: str = C["grid"]) -> dict:
    return dict(gridcolor=gridcolor, zerolinecolor=gridcolor, linecolor=gridcolor)


# ── Measurement & probability ─────────────────────────────────────────────────

def measurement_bar_chart(counts: dict, shots: int, title: str = "Measurement Counts") -> go.Figure:
    states = list(counts.keys())
    values = list(counts.values())
    probs  = [v / shots for v in values]
    fig = go.Figure(go.Bar(
        x=states, y=values,
        text=[f"{p:.1%}" for p in probs], textposition="outside",
        marker=dict(
            color=values,
            colorscale=[[0, C["primary"]], [1, C["secondary"]]],
            showscale=False, line=dict(color=C["secondary"], width=0.8),
        ),
        hovertemplate="<b>|%{x}⟩</b><br>Count: %{y}<br>Prob: %{text}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=C["secondary"])),
        xaxis=dict(title="State", **_axis(), tickfont=dict(family="monospace", size=10)),
        yaxis=dict(title="Count", **_axis()),
        showlegend=False, **_BASE_LAYOUT,
    )
    return fig


def probability_chart(counts: dict, shots: int, title: str = "Probability Distribution") -> go.Figure:
    states = list(counts.keys())
    probs  = [v / shots for v in counts.values()]
    max_p  = max(probs) if probs else 1.0
    fig = go.Figure(go.Bar(
        x=probs, y=states, orientation="h",
        text=[f"{p:.4f}" for p in probs], textposition="outside",
        marker=dict(
            color=probs, colorscale=[[0, C["card"]], [1, C["accent"]]],
            showscale=False, line=dict(color=C["accent"], width=0.8),
        ),
        hovertemplate="<b>|%{y}⟩</b><br>Prob: %{x:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=C["secondary"])),
        xaxis=dict(title="Probability", range=[0, max_p * 1.25], **_axis()),
        yaxis=dict(title="State", **_axis()),
        showlegend=False, **_BASE_LAYOUT,
    )
    return fig


def entropy_gauge(entropy: float, max_entropy: float = 1.0, title: str = "Bit Entropy") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=round(entropy, 4),
        title={"text": title, "font": {"color": C["text"], "size": 14}},
        number={"font": {"color": C["secondary"]}, "suffix": " bits/sym"},
        gauge={
            "axis": {"range": [0, max_entropy], "tickcolor": C["muted"]},
            "bar": {"color": C["primary"], "thickness": 0.28},
            "bgcolor": C["card"], "borderwidth": 1, "bordercolor": C["grid"],
            "steps": [
                {"range": [0, max_entropy * 0.33], "color": "#1a0a0a"},
                {"range": [max_entropy * 0.33, max_entropy * 0.66], "color": "#181806"},
                {"range": [max_entropy * 0.66, max_entropy], "color": "#0a1a10"},
            ],
            "threshold": {"line": {"color": C["accent"], "width": 3}, "thickness": 0.8, "value": entropy},
        },
    ))
    fig.update_layout(paper_bgcolor=C["bg"], font=dict(color=C["text"]),
                      height=240, margin=dict(l=24, r=24, t=48, b=16))
    return fig


def session_validity_gauge(fraction: float, minutes: int, seconds: int) -> go.Figure:
    pct = min(100.0, fraction * 100)
    bar_color = C["accent"] if pct > 25 else C["danger"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=round(pct, 1),
        title={"text": f"Session — {minutes}m {seconds}s left", "font": {"color": C["text"], "size": 13}},
        number={"font": {"color": bar_color}, "suffix": "%"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": C["muted"]},
            "bar": {"color": bar_color, "thickness": 0.28},
            "bgcolor": C["card"], "borderwidth": 1, "bordercolor": C["grid"],
            "steps": [
                {"range": [0, 25], "color": "#1a0808"},
                {"range": [25, 60], "color": "#111108"},
                {"range": [60, 100], "color": "#081a0e"},
            ],
        },
    ))
    fig.update_layout(paper_bgcolor=C["bg"], font=dict(color=C["text"]),
                      height=240, margin=dict(l=24, r=24, t=48, b=16))
    return fig


def token_bit_distribution(bitstring: str) -> go.Figure:
    ones = bitstring.count("1")
    zeros = bitstring.count("0")
    fig = go.Figure(go.Pie(
        labels=["|1⟩ measured", "|0⟩ measured"], values=[ones, zeros], hole=0.52,
        marker=dict(colors=[C["primary"], C["grid"]], line=dict(color=C["secondary"], width=1.5)),
        textinfo="label+percent", textfont=dict(color=C["text"], size=12),
        hovertemplate="%{label}: %{value} qubits (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Qubit State Distribution", font=dict(size=13, color=C["secondary"])),
        paper_bgcolor=C["bg"], font=dict(color=C["text"]),
        height=260, showlegend=False, margin=dict(l=16, r=16, t=44, b=16),
    )
    return fig


def randomness_histogram(classical: np.ndarray, quantum: np.ndarray, n_bins: int = 32) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=classical, nbinsx=n_bins, name="Classical (NumPy)",
                               marker_color=C["amber"], opacity=0.72,
                               hovertemplate="Value: %{x}<br>Count: %{y}<extra></extra>"))
    fig.add_trace(go.Histogram(x=quantum,   nbinsx=n_bins, name="Quantum (Qiskit)",
                               marker_color=C["primary"], opacity=0.72,
                               hovertemplate="Value: %{x}<br>Count: %{y}<extra></extra>"))
    fig.update_layout(
        barmode="overlay",
        title=dict(text="Distribution Overlap — Classical vs Quantum", font=dict(size=14, color=C["secondary"])),
        xaxis=dict(title="Sample Value", **_axis()),
        yaxis=dict(title="Frequency", **_axis()),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C["grid"], font=dict(color=C["text"])),
        **_BASE_LAYOUT,
    )
    return fig


def entropy_comparison_bar(classical_h: float, quantum_h: float) -> go.Figure:
    top = max(classical_h, quantum_h, 0.1) * 1.3
    fig = go.Figure(go.Bar(
        x=["Classical (NumPy PRNG)", "Quantum (Qiskit Aer)"],
        y=[classical_h, quantum_h],
        marker=dict(color=[C["amber"], C["primary"]],
                    line=dict(color=[C["text"], C["secondary"]], width=1)),
        text=[f"{classical_h:.4f} bits", f"{quantum_h:.4f} bits"],
        textposition="outside",
        hovertemplate="%{x}<br>H = %{y:.4f} bits<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Shannon Entropy Comparison", font=dict(size=14, color=C["secondary"])),
        xaxis=dict(**_axis()),
        yaxis=dict(title="Shannon Entropy (bits)", range=[0, top], **_axis()),
        showlegend=False, **_BASE_LAYOUT,
    )
    return fig


def sequence_scatter(classical: np.ndarray, quantum: np.ndarray, n_show: int = 200) -> go.Figure:
    x = list(range(n_show))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=classical[:n_show].tolist(), mode="lines",
                             name="Classical", line=dict(color=C["amber"], width=1), opacity=0.85))
    fig.add_trace(go.Scatter(x=x, y=quantum[:n_show].tolist(),   mode="lines",
                             name="Quantum",   line=dict(color=C["primary"], width=1), opacity=0.85))
    fig.update_layout(
        title=dict(text=f"First {n_show} Samples — Sequential View", font=dict(size=14, color=C["secondary"])),
        xaxis=dict(title="Sample Index", **_axis()),
        yaxis=dict(title="Value", **_axis()),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C["grid"], font=dict(color=C["text"])),
        **_BASE_LAYOUT,
    )
    return fig


# ── Bloch sphere & state visualization ───────────────────────────────────────

def state_vector_2d(
    bloch_init: tuple,
    bloch_final: tuple | None = None,
    label_init: str = "Initial state",
    label_final: str = "After gate",
) -> go.Figure:
    """
    2D cross-section of the Bloch sphere (xz-plane, ignoring y/phi component).

    Maps Bloch vector (bx, by, bz) → plot point (bx, bz):
      |0⟩ (0,0,+1) → top    |1⟩ (0,0,-1) → bottom
      |+⟩ (+1,0,0) → right  |−⟩ (-1,0,0) → left
    """
    t = np.linspace(0, 2 * np.pi, 300)
    fig = go.Figure()

    # ── Outer ring ────────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=np.cos(t), y=np.sin(t), mode="lines",
        line=dict(color=C["grid"], width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # ── Dashed axes ───────────────────────────────────────────────────────────
    for xs, ys in [([-1.28, 1.28], [0, 0]), ([0, 0], [-1.28, 1.28])]:
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines",
            line=dict(color=C["muted"], width=1, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))

    # ── Key-state labels and anchor dots ─────────────────────────────────────
    labels = {"|0⟩": (0, 1.38), "|1⟩": (0, -1.38),
              "|+⟩": (1.38, 0), "|−⟩": (-1.38, 0)}
    anchors = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for txt, (lx, ly) in labels.items():
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly], mode="text",
            text=[txt], textfont=dict(color=C["muted"], size=13, family="monospace"),
            showlegend=False, hoverinfo="skip",
        ))
    fig.add_trace(go.Scatter(
        x=[a[0] for a in anchors], y=[a[1] for a in anchors], mode="markers",
        marker=dict(size=5, color=C["muted"]),
        showlegend=False, hoverinfo="skip",
    ))

    # ── State vectors ─────────────────────────────────────────────────────────
    xi, _, zi = bloch_init
    has_final  = bloch_final is not None
    p0_i, p1_i = (1 + zi) / 2, (1 - zi) / 2

    fig.add_trace(go.Scatter(
        x=[0, xi], y=[0, zi], mode="lines+markers",
        line=dict(color=C["secondary"], width=4 if not has_final else 2,
                  dash="solid" if not has_final else "dot"),
        marker=dict(size=[4, 12 if not has_final else 8], color=C["secondary"]),
        name=label_init,
        hovertemplate=(
            f"<b>{label_init}</b><br>P(|0⟩) = {p0_i:.3f}<br>P(|1⟩) = {p1_i:.3f}<extra></extra>"
        ),
    ))

    title_text = f"{label_init}: P(|0⟩) = {p0_i:.3f}  |  P(|1⟩) = {p1_i:.3f}"

    if has_final:
        xf, _, zf = bloch_final
        p0_f, p1_f = (1 + zf) / 2, (1 - zf) / 2
        fig.add_trace(go.Scatter(
            x=[0, xf], y=[0, zf], mode="lines+markers",
            line=dict(color=C["accent"], width=4),
            marker=dict(size=[4, 12], color=C["accent"]),
            name=label_final,
            hovertemplate=(
                f"<b>{label_final}</b><br>P(|0⟩) = {p0_f:.3f}<br>P(|1⟩) = {p1_f:.3f}<extra></extra>"
            ),
        ))
        title_text = (
            f"{label_init} → {label_final}  |  "
            f"P(|0⟩): {p0_i:.3f} → {p0_f:.3f}  |  P(|1⟩): {p1_i:.3f} → {p1_f:.3f}"
        )

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=12, color=C["secondary"])),
        **_BASE_LAYOUT,
        height=370,
        xaxis=dict(range=[-1.55, 1.55], showgrid=False, zeroline=False,
                   showticklabels=False, scaleanchor="y"),
        yaxis=dict(range=[-1.55, 1.55], showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["text"])),
        margin=dict(l=16, r=16, t=56, b=16),
    )
    return fig


def state_probability_bars(
    p0_init: float, p1_init: float,
    p0_final: float | None = None, p1_final: float | None = None,
    label_init: str = "Initial", label_final: str = "After gate",
) -> go.Figure:
    """Grouped bar chart showing P(|0⟩) and P(|1⟩) before and after a gate."""
    has_final = p0_final is not None
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["|0⟩", "|1⟩"], y=[p0_init, p1_init],
        name=label_init,
        marker=dict(color=[C["secondary"], C["primary"]],
                    line=dict(color=C["grid"], width=1)),
        opacity=0.75 if has_final else 1.0,
        text=[f"{p0_init:.3f}", f"{p1_init:.3f}"], textposition="outside",
    ))
    if has_final:
        fig.add_trace(go.Bar(
            x=["|0⟩", "|1⟩"], y=[p0_final, p1_final],
            name=label_final,
            marker=dict(color=[C["accent"], C["amber"]],
                        line=dict(color=C["grid"], width=1)),
            text=[f"{p0_final:.3f}", f"{p1_final:.3f}"], textposition="outside",
        ))
        fig.update_layout(barmode="group")
    fig.update_layout(
        title=dict(text="Measurement Probabilities", font=dict(size=13, color=C["secondary"])),
        xaxis=dict(**_axis()), yaxis=dict(title="Probability", range=[0, 1.3], **_axis()),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["text"])),
        **_BASE_LAYOUT, height=300,
    )
    return fig


# ── Noise simulation & experiment analytics ───────────────────────────────────

def noise_comparison_grouped(
    clean: dict, noisy: dict, shots: int,
    title: str = "Clean vs Noisy Circuit",
) -> go.Figure:
    """Grouped bar chart comparing measurement distributions with and without noise."""
    all_states  = sorted(set(clean) | set(noisy))
    clean_probs = [clean.get(s, 0) / shots for s in all_states]
    noisy_probs = [noisy.get(s, 0) / shots for s in all_states]
    max_p       = max(max(clean_probs, default=0), max(noisy_probs, default=0), 0.01)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=all_states, y=clean_probs, name="Clean (no noise)",
        marker=dict(color=C["accent"], line=dict(color=C["accent"], width=1)),
        text=[f"{p:.3f}" for p in clean_probs], textposition="outside",
        hovertemplate="<b>|%{x}⟩</b> Clean: %{y:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=all_states, y=noisy_probs, name="Noisy",
        marker=dict(color=C["danger"], line=dict(color=C["danger"], width=1)),
        text=[f"{p:.3f}" for p in noisy_probs], textposition="outside",
        hovertemplate="<b>|%{x}⟩</b> Noisy: %{y:.4f}<extra></extra>",
    ))
    fig.update_layout(
        barmode="group",
        title=dict(text=title, font=dict(size=14, color=C["secondary"])),
        xaxis=dict(title="Measurement State", **_axis()),
        yaxis=dict(title="Probability", range=[0, min(1.3, max_p * 1.4)], **_axis()),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["text"])),
        **_BASE_LAYOUT,
    )
    return fig


def tvd_gauge(tvd_value: float, title: str = "Noise Distortion (TVD)") -> go.Figure:
    """Gauge showing Total Variation Distance between clean and noisy outputs (range 0–1)."""
    color = C["accent"] if tvd_value < 0.08 else (C["amber"] if tvd_value < 0.22 else C["danger"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=round(tvd_value, 4),
        title={"text": title, "font": {"color": C["text"], "size": 13}},
        number={"font": {"color": color}, "valueformat": ".4f"},
        gauge={
            "axis": {"range": [0, 1.0], "tickcolor": C["muted"]},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": C["card"], "borderwidth": 1, "bordercolor": C["grid"],
            "steps": [
                {"range": [0.00, 0.08], "color": "#081a0e"},
                {"range": [0.08, 0.22], "color": "#1a1406"},
                {"range": [0.22, 1.00], "color": "#1a0808"},
            ],
        },
    ))
    fig.update_layout(paper_bgcolor=C["bg"], font=dict(color=C["text"]),
                      height=220, margin=dict(l=24, r=24, t=44, b=8))
    return fig


def experiment_type_donut(type_counts: dict) -> go.Figure:
    """Donut chart showing experiment count by type."""
    labels = list(type_counts.keys())
    values = list(type_counts.values())
    colors = [C["primary"], C["accent"], C["amber"], C["secondary"], C["cyan"], C["danger"]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.52,
        marker=dict(colors=colors[:len(labels)], line=dict(color=C["grid"], width=1.5)),
        textinfo="label+percent", textfont=dict(color=C["text"], size=12),
        hovertemplate="%{label}: %{value} run(s)<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Experiments by Type", font=dict(size=13, color=C["secondary"])),
        paper_bgcolor=C["bg"], font=dict(color=C["text"]),
        height=280, showlegend=False, margin=dict(l=16, r=16, t=44, b=16),
    )
    return fig


def measurement_sim_bars(counts: dict, shots: int, p0_theory: float, p1_theory: float) -> go.Figure:
    """Bar chart comparing simulated measurement vs theoretical probabilities."""
    measured_0 = counts.get("0", 0) / shots
    measured_1 = counts.get("1", 0) / shots
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["|0⟩", "|1⟩"], y=[measured_0, measured_1],
        name="Measured", marker=dict(color=C["primary"], line=dict(color=C["secondary"], width=1)),
        text=[f"{measured_0:.3f}", f"{measured_1:.3f}"], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=["|0⟩", "|1⟩"], y=[p0_theory, p1_theory],
        name="Theoretical", marker=dict(color=C["accent"], line=dict(color=C["accent"], width=1)),
        text=[f"{p0_theory:.3f}", f"{p1_theory:.3f}"], textposition="outside",
        opacity=0.6,
    ))
    fig.update_layout(
        barmode="group",
        title=dict(text="Measured vs Theoretical Probabilities", font=dict(size=13, color=C["secondary"])),
        xaxis=dict(**_axis()), yaxis=dict(title="Probability", range=[0, 1.3], **_axis()),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["text"])),
        **_BASE_LAYOUT, height=320,
    )
    return fig
