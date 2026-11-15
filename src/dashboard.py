"""Build an interactive HTML dashboard and a static PNG from results/footprint_scenarios.csv."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ["N2O direct", "N2O indirect", "Urea CO2", "N manufacture", "Lime CO2",
           "Diesel", "Electricity"]
COLORS = ["#b71c1c", "#e57373", "#f9a825", "#6d4c41", "#9e9e9e", "#1565c0", "#4caf50"]


def main():
    res = pd.read_csv(ROOT / "results" / "footprint_scenarios.csv")
    farms = res["farm"].unique().tolist()

    fig = make_subplots(rows=1, cols=len(farms), subplot_titles=farms, shared_yaxes=False)
    for j, farm in enumerate(farms, start=1):
        sub = res[res["farm"] == farm]
        for src, col in zip(SOURCES, COLORS):
            fig.add_trace(go.Bar(
                x=sub["scenario"], y=sub[src], name=src, marker_color=col,
                legendgroup=src, showlegend=(j == 1),
                customdata=sub[["total_kg_co2e_ha", "kg_co2e_per_t", "change_vs_baseline_pct"]],
                hovertemplate=("<b>%{x}</b><br>" + src + ": %{y:,.0f} kg CO2e/ha<br>"
                               "Total: %{customdata[0]:,.0f} kg CO2e/ha<br>"
                               "Per tonne: %{customdata[1]:,.0f} kg CO2e/t<br>"
                               "Change vs baseline: %{customdata[2]}%<extra></extra>")),
                row=1, col=j)
    fig.update_layout(barmode="stack", height=560, template="plotly_white",
                      title="AgroCarbon: farm greenhouse-gas footprint by source and scenario "
                            "(example inputs)",
                      yaxis_title="kg CO2e per hectare")
    fig.write_html(ROOT / "results" / "dashboard.html", include_plotlyjs="cdn")

    fig2, axes = plt.subplots(1, len(farms), figsize=(7 * len(farms), 5))
    for ax, farm in zip(axes, farms):
        sub = res[res["farm"] == farm].set_index("scenario")[SOURCES]
        sub.plot.barh(stacked=True, ax=ax, color=COLORS, legend=False)
        ax.set_title(farm)
        ax.set_xlabel("kg CO2e per hectare")
        ax.invert_yaxis()
    handles, labels = axes[0].get_legend_handles_labels()
    fig2.legend(handles, labels, loc="lower center", ncol=len(SOURCES), fontsize=9)
    fig2.suptitle("Greenhouse-gas footprint by source and scenario (example inputs)")
    fig2.tight_layout(rect=(0, 0.07, 1, 1))
    fig2.savefig(ROOT / "results" / "footprint_scenarios.png", dpi=150)
    print("Wrote results/dashboard.html and results/footprint_scenarios.png")


if __name__ == "__main__":
    main()
