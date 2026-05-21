"""
Experiment Dashboard
====================
Aggregates all experiment runs from session state, shows summary analytics,
enables rerun of any previous configuration, and exports results to JSON/CSV.
"""

import csv
import io
import json
import datetime
import streamlit as st
import pandas as pd

from visualizations.charts import experiment_type_donut
from utils.helpers import get_experiment_log, clear_experiment_log


# ── Export helpers ────────────────────────────────────────────────────────────

def _to_json(experiments: list) -> str:
    def _fmt(e: dict) -> dict:
        return {
            "id":        e["id"],
            "timestamp": datetime.datetime.fromtimestamp(e["timestamp"]).isoformat(),
            "type":      e["type"],
            "label":     e["label"],
            "config":    e["config"],
            "metrics":   e["metrics"],
        }
    return json.dumps([_fmt(e) for e in experiments], indent=2)


def _to_csv(experiments: list) -> str:
    if not experiments:
        return ""
    rows = []
    for e in experiments:
        row: dict = {
            "id":        e["id"],
            "timestamp": datetime.datetime.fromtimestamp(e["timestamp"]).isoformat(),
            "type":      e["type"],
            "label":     e["label"],
        }
        for k, v in e.get("metrics", {}).items():
            row[f"metric_{k}"] = v
        for k, v in e.get("config", {}).items():
            if not isinstance(v, (list, dict)):
                row[f"config_{k}"] = v
        rows.append(row)

    # Build unified fieldname order
    all_keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in all_keys:
                all_keys.append(k)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=all_keys, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


# ── Rerun helpers ─────────────────────────────────────────────────────────────

def _load_circuit_rerun(config: dict) -> None:
    """Pre-populate Circuit Playground state so the user can rerun it."""
    st.session_state["cp_gates"]       = config.get("gates", [])
    st.session_state["cp_prev_qubits"] = config.get("n_qubits", 2)
    st.session_state["cp_results"]     = None
    st.success("Circuit loaded into Circuit Playground. Navigate there to run it.")


def _load_noise_rerun(config: dict) -> None:
    """Pre-populate Noise Simulator state."""
    st.session_state["ns_rerun_cfg"] = config
    st.success("Noise config loaded. Navigate to Noise Simulator to run it.")


# ── Summary card ──────────────────────────────────────────────────────────────

def _summary_section(experiments: list) -> None:
    total = len(experiments)
    by_type: dict[str, int] = {}
    for e in experiments:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Runs",    total)
    m2.metric("Module Types", len(by_type))
    m3.metric("Most Frequent", max(by_type, key=by_type.get) if by_type else "—")
    m4.metric("Log Limit",     "30 per session")

    if by_type:
        st.plotly_chart(experiment_type_donut(by_type), use_container_width=False)


# ── Experiment history table ──────────────────────────────────────────────────

_TYPE_COLORS = {
    "Circuit":    "#a78bfa",
    "Token":      "#10b981",
    "Noise":      "#ef4444",
    "Randomness": "#f59e0b",
}


def _history_table(experiments: list) -> None:
    if not experiments:
        st.markdown(
            '<div style="text-align:center; padding:40px; color:#2d2d4e;">'
            'No experiments yet. Run a simulation in any module to log it here.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    for exp in experiments:
        color = _TYPE_COLORS.get(exp["type"], "#64748b")
        ts    = datetime.datetime.fromtimestamp(exp["timestamp"]).strftime("%H:%M:%S")

        # Metric pills
        metrics_html = " ".join(
            f'<span style="background:rgba(255,255,255,0.04); border:1px solid #2d2d4e; '
            f'border-radius:4px; padding:1px 8px; font-size:0.78em; color:#64748b; font-family:monospace;">'
            f'{k}={v}</span>'
            for k, v in exp["metrics"].items()
        )

        card_html = (
            f'<div style="background:rgba(22,22,41,0.7); border:1px solid {color}33; '
            f'border-left:3px solid {color}; border-radius:8px; padding:12px 16px; margin-bottom:8px; '
            f'display:flex; align-items:center; gap:14px;">'
            f'<span style="color:#2d2d4e; font-size:0.75em; min-width:36px;">#{exp["id"]}</span>'
            f'<span style="background:{color}22; color:{color}; border-radius:4px; padding:2px 8px; '
            f'font-size:0.78em; font-weight:600; min-width:70px; text-align:center;">{exp["type"]}</span>'
            f'<span style="color:#94a3b8; font-size:0.88em; flex:1;">{exp["label"]}</span>'
            f'<span style="color:#2d2d4e; font-size:0.78em; min-width:60px;">{ts}</span>'
            f'<span>{metrics_html}</span>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        # Detail expander with rerun
        with st.expander(f"  Details & Rerun — Experiment #{exp['id']}"):
            detail_l, detail_r = st.columns(2)
            with detail_l:
                st.markdown("**Configuration**")
                for k, v in exp["config"].items():
                    if isinstance(v, list):
                        st.markdown(f"- `{k}`: {len(v)} items")
                    else:
                        st.markdown(f"- `{k}`: `{v}`")
            with detail_r:
                st.markdown("**Metrics**")
                for k, v in exp["metrics"].items():
                    st.markdown(f"- `{k}`: `{v}`")

            if exp["type"] == "Circuit":
                if st.button(f"↺  Load into Circuit Playground", key=f"rerun_circ_{exp['id']}"):
                    _load_circuit_rerun(exp["config"])
                    st.rerun()

            elif exp["type"] == "Noise":
                if st.button(f"↺  Load into Noise Simulator", key=f"rerun_noise_{exp['id']}"):
                    _load_noise_rerun(exp["config"])
                    st.rerun()


# ── Export section ────────────────────────────────────────────────────────────

def _export_section(experiments: list) -> None:
    if not experiments:
        st.info("Run some experiments first to enable export.")
        return

    st.markdown("### Export")
    exp_col, csv_col, clear_col = st.columns([1, 1, 1])

    with exp_col:
        json_bytes = _to_json(experiments).encode("utf-8")
        st.download_button(
            label="⬇ Download JSON",
            data=json_bytes,
            file_name=f"quantum_lab_experiments_{datetime.date.today()}.json",
            mime="application/json",
            use_container_width=True,
        )

    with csv_col:
        csv_str   = _to_csv(experiments)
        csv_bytes = csv_str.encode("utf-8")
        st.download_button(
            label="⬇ Download CSV",
            data=csv_bytes,
            file_name=f"quantum_lab_experiments_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with clear_col:
        if st.button("🗑 Clear History", use_container_width=True):
            clear_experiment_log()
            st.rerun()

    # Preview table
    with st.expander("Preview export data"):
        rows = [
            {
                "ID":        e["id"],
                "Time":      datetime.datetime.fromtimestamp(e["timestamp"]).strftime("%H:%M:%S"),
                "Type":      e["type"],
                "Label":     e["label"],
                **{f"m_{k}": v for k, v in e["metrics"].items()},
            }
            for e in experiments
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ── Main render ───────────────────────────────────────────────────────────────

def render_experiment_dashboard() -> None:
    st.markdown("## 📊 Experiment Dashboard")
    st.markdown(
        "*All simulation runs from this session, with summary analytics, "
        "per-experiment details, rerun capability, and JSON/CSV export.*"
    )

    experiments = get_experiment_log()

    st.divider()
    st.markdown("### Session Summary")
    _summary_section(experiments)

    st.divider()
    st.markdown("### Experiment History")
    st.caption("Newest first · up to 30 entries · clears on page refresh")
    _history_table(experiments)

    st.divider()
    _export_section(experiments)

    with st.expander("📖 How experiment logging works"):
        st.markdown("""
**What gets logged automatically:**

| Module | Event logged |
|---|---|
| Quantum Auth Lab | Successful login (token generation) |
| Circuit Playground | Every simulation run |
| Noise Simulator | Every noise comparison run |
| Randomness Analyzer | Every generate-and-compare run |

**Storage:** All experiment data is held in Streamlit's `st.session_state` — it persists
for the browser session but is cleared on page refresh. Use the export buttons to save
results before closing.

**Rerun:** Loading a previous Circuit or Noise experiment pre-populates the module's
form fields. Navigate to the relevant module and click Run to reproduce the result
(quantum measurement has inherent randomness, so outputs may differ slightly).
        """)
