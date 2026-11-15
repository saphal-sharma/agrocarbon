"""
AgroCarbon: farm-level greenhouse-gas footprint calculator with intervention scenarios.

Sources covered (per hectare, then per tonne of product):
  * direct and indirect N2O from synthetic nitrogen (IPCC Tier 1)
  * CO2 from urea hydrolysis and from liming
  * CO2 from diesel use
  * CO2e from electricity (e.g. irrigation pumps, drying)
  * upstream CO2e from nitrogen fertilizer manufacture (user-supplied factor)

Usage:
    python src/footprint.py                         # example farms
    python src/footprint.py my_farms.csv            # your own farms
"""
from __future__ import annotations

import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import pandas as pd

from factors import C_TO_CO2, N2O_N_TO_N2O, UREA_N_CONTENT, f

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class FarmActivity:
    farm: str
    crop: str
    yield_t_ha: float
    n_urea_kg_ha: float          # kg N applied as urea
    n_other_kg_ha: float         # kg N from other synthetic fertilizers (AN, CAN, NPK...)
    lime_t_ha: float             # t limestone per ha per year
    diesel_l_ha: float
    electricity_kwh_ha: float
    grid_ef_kg_kwh: float        # kg CO2e per kWh (user input)
    n_manufacture_ef: float      # kg CO2e per kg N manufactured (user input)

    @property
    def n_total(self) -> float:
        return self.n_urea_kg_ha + self.n_other_kg_ha


def emissions(a: FarmActivity) -> dict:
    """kg CO2e per hectare by source."""
    gwp = f("GWP_N2O")
    n = a.n_total
    direct = n * f("EF1_direct_n2o") * N2O_N_TO_N2O * gwp
    volat = n * f("FRAC_GASF") * f("EF4_volatilisation") * N2O_N_TO_N2O * gwp
    leach = n * f("FRAC_LEACH") * f("EF5_leaching") * N2O_N_TO_N2O * gwp
    urea_t = a.n_urea_kg_ha / UREA_N_CONTENT / 1000
    urea_co2 = urea_t * f("EF_urea") * C_TO_CO2 * 1000
    lime_co2 = a.lime_t_ha * f("EF_limestone") * C_TO_CO2 * 1000
    return {
        "N2O direct": direct,
        "N2O indirect": volat + leach,
        "Urea CO2": urea_co2,
        "Lime CO2": lime_co2,
        "N manufacture": n * a.n_manufacture_ef,
        "Diesel": a.diesel_l_ha * f("EF_diesel"),
        "Electricity": a.electricity_kwh_ha * a.grid_ef_kg_kwh,
    }


def summarise(a: FarmActivity, scenario: str = "Baseline") -> dict:
    e = emissions(a)
    total = sum(e.values())
    n_related = sum(v for k, v in e.items() if k.startswith(("N2O", "Urea", "N manufacture")))
    return {"farm": a.farm, "scenario": scenario, **{k: round(v, 1) for k, v in e.items()},
            "total_kg_co2e_ha": round(total, 1),
            "kg_co2e_per_t": round(total / a.yield_t_ha, 1),
            "n_related_share_pct": round(100 * n_related / total, 1)}


def scenarios(a: FarmActivity, n_cut: float = 0.20, yield_loss_from_n_cut: float = 0.0,
              diesel_cut: float = 0.30) -> list[tuple[str, FarmActivity]]:
    """Intervention scenarios. Effect sizes are assumptions to be set by the user."""
    return [
        ("Baseline", a),
        (f"N rate -{n_cut:.0%}", replace(a, n_urea_kg_ha=a.n_urea_kg_ha * (1 - n_cut),
                                         n_other_kg_ha=a.n_other_kg_ha * (1 - n_cut),
                                         yield_t_ha=a.yield_t_ha * (1 - yield_loss_from_n_cut))),
        ("Urea replaced by other N", replace(a, n_urea_kg_ha=0, n_other_kg_ha=a.n_total)),
        (f"Reduced tillage (diesel -{diesel_cut:.0%})", replace(a, diesel_l_ha=a.diesel_l_ha * (1 - diesel_cut))),
        ("Renewable electricity", replace(a, grid_ef_kg_kwh=0.0)),
    ]


def run(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, comment="#")
    rows = []
    for rec in df.to_dict("records"):
        a = FarmActivity(**rec)
        for name, s in scenarios(a):
            rows.append(summarise(s, name))
    return pd.DataFrame(rows)


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "examples" / "example_farms.csv"
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    res = run(path)
    base = res[res["scenario"] == "Baseline"].set_index("farm")
    res["change_vs_baseline_pct"] = res.apply(
        lambda r: round(100 * (r["total_kg_co2e_ha"] / base.loc[r["farm"], "total_kg_co2e_ha"] - 1), 1),
        axis=1)
    res.to_csv(out / "footprint_scenarios.csv", index=False)
    pd.set_option("display.width", 200)
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
