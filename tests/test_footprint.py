"""Unit tests: hand-calculated values for the IPCC Tier 1 equations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from footprint import FarmActivity, emissions  # noqa: E402


def make(**kw):
    base = dict(farm="t", crop="c", yield_t_ha=1.0, n_urea_kg_ha=0, n_other_kg_ha=0,
                lime_t_ha=0, diesel_l_ha=0, electricity_kwh_ha=0, grid_ef_kg_kwh=0,
                n_manufacture_ef=0)
    base.update(kw)
    return FarmActivity(**base)


def test_direct_n2o_100kg():
    # 100 kg N x 0.01 x 44/28 x 273 = 429.0 kg CO2e
    e = emissions(make(n_other_kg_ha=100))
    assert abs(e["N2O direct"] - 429.0) < 0.1


def test_indirect_n2o_100kg():
    # 100 x (0.11*0.010 + 0.24*0.011) x 44/28 x 273 = 160.4 kg CO2e
    e = emissions(make(n_other_kg_ha=100))
    assert abs(e["N2O indirect"] - 160.4) < 0.1


def test_urea_co2():
    # 46 kg N as urea = 100 kg urea -> 0.1 t x 0.20 x 44/12 = 0.0733 t = 73.3 kg CO2
    e = emissions(make(n_urea_kg_ha=46))
    assert abs(e["Urea CO2"] - 73.3) < 0.1


def test_lime_and_diesel():
    e = emissions(make(lime_t_ha=1.0, diesel_l_ha=10))
    assert abs(e["Lime CO2"] - 440.0) < 0.1      # 1 t x 0.12 x 44/12
    assert abs(e["Diesel"] - 26.8) < 0.01
