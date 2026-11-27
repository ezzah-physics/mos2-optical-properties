"""Regenerate the figures for the MoS2 layer-dependent optical properties project.

Usage (from the repository root):
    python src/plot_figures.py

Reads the CSV files in data/ and writes PNG files to figures/.
No value is estimated or averaged here: every number plotted comes
directly from the CSV files (see README for sources).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

MARKERS = {"Mak 2010": "o", "Scheuschner 2014": "s", "Li 2014": "^"}
# Small horizontal offsets so points from different papers do not overlap
OFFSETS = {"Mak 2010": -0.12, "Scheuschner 2014": 0.0, "Li 2014": 0.12}
COLORS = {"direct": "tab:blue", "indirect": "tab:red"}


def load_energies() -> pd.DataFrame:
    df = pd.read_csv(DATA / "mos2_optical_data.csv")
    # Place "bulk" at the right of the x axis
    df["x"] = df["layers"].apply(lambda v: 8 if v == "bulk" else int(v))
    df["digitised"] = df["source_type"].str.contains("digitised")
    return df


def fig1_energy_vs_layers(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.3))
    for _, r in df.iterrows():
        ax.errorbar(
            r["x"] + OFFSETS[r["source"]], r["energy_eV"],
            yerr=None if pd.isna(r["uncertainty_eV"]) else r["uncertainty_eV"],
            marker=MARKERS[r["source"]], color=COLORS[r["transition_type"]],
            markerfacecolor="white" if r["digitised"] else COLORS[r["transition_type"]],
            markersize=8, capsize=3, linestyle="none",
        )
    ax.set_xticks(list(range(1, 7)) + [8])
    ax.set_xticklabels([str(i) for i in range(1, 7)] + ["Bulk"])
    ax.set_xlabel("Number of layers")
    ax.set_ylabel("Energy of lowest optical transition (eV)")
    ax.set_title("MoS$_2$: reported lowest optical transition vs. layers")
    # Legend entries
    for t, c in COLORS.items():
        ax.plot([], [], "o", color=c, label=f"{t} transition")
    for s, m in MARKERS.items():
        ax.plot([], [], m, color="gray", label=s)
    ax.plot([], [], "o", color="gray", markerfacecolor="white",
            label="digitised from figure")
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_energy_vs_layers.png", dpi=200)
    plt.close(fig)


def fig2_monolayer(df: pd.DataFrame) -> None:
    mono = df[df["layers"] == "1"].reset_index(drop=True)
    labels = [f"{r.source}\n{r.quantity}" for r in mono.itertuples()]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.barh(
        range(len(mono)), mono["energy_eV"],
        xerr=mono["uncertainty_eV"].fillna(0), color="tab:blue", alpha=0.8,
    )
    ax.set_yticks(range(len(mono)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(1.7, 1.95)
    ax.set_xlabel("Energy (eV)")
    ax.set_title("Monolayer MoS$_2$: values reported by each source")
    fig.tight_layout()
    fig.savefig(OUT / "fig2_monolayer_comparison.png", dpi=200)
    plt.close(fig)


def fig3_quantum_yield() -> None:
    qy = pd.read_csv(DATA / "mos2_quantum_yield.csv")
    fig, ax = plt.subplots(figsize=(5.5, 4.2))
    for _, r in qy.iterrows():
        n = int(r["layers"])
        if pd.isna(r["quantum_yield_low"]):  # monolayer: single maximum value
            ax.plot(n, r["quantum_yield_high"], "o", color="tab:blue", markersize=8)
        else:  # range given as an order of magnitude
            ax.vlines(n, r["quantum_yield_low"], r["quantum_yield_high"],
                      color="tab:red", linewidth=6, alpha=0.7)
    ax.set_yscale("log")
    ax.set_xlabel("Number of layers N")
    ax.set_ylabel("PL quantum yield")
    ax.set_title("Suspended MoS$_2$ (Mak et al. 2010)")
    fig.tight_layout()
    fig.savefig(OUT / "fig3_quantum_yield.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    energies = load_energies()
    fig1_energy_vs_layers(energies)
    fig2_monolayer(energies)
    fig3_quantum_yield()
    print(f"Figures written to {OUT}")
