"""Emission factors (IPCC Tier 1 defaults unless stated otherwise).

Every number is listed with its source so users can check and replace it.
Factors marked USER_INPUT are site- or product-specific and must be supplied.
"""

FACTORS = {
    # --- Nitrous oxide from managed soils: IPCC (2019) Refinement, Vol. 4, Ch. 11
    "EF1_direct_n2o": {
        "value": 0.010, "unit": "kg N2O-N per kg N applied",
        "source": "IPCC 2019 Refinement, Vol.4 Ch.11, Table 11.1 (aggregated default EF1)"},
    "FRAC_GASF": {
        "value": 0.11, "unit": "fraction of synthetic N volatilised as NH3 and NOx",
        "source": "IPCC 2019 Refinement, Vol.4 Ch.11, Table 11.3"},
    "EF4_volatilisation": {
        "value": 0.010, "unit": "kg N2O-N per kg N volatilised",
        "source": "IPCC 2019 Refinement, Vol.4 Ch.11, Table 11.3"},
    "FRAC_LEACH": {
        "value": 0.24, "unit": "fraction of N lost by leaching/runoff (wet climates)",
        "source": "IPCC 2019 Refinement, Vol.4 Ch.11, Table 11.3"},
    "EF5_leaching": {
        "value": 0.011, "unit": "kg N2O-N per kg N leached",
        "source": "IPCC 2019 Refinement, Vol.4 Ch.11, Table 11.3"},
    # --- CO2 from urea and lime: IPCC 2006 Guidelines, Vol. 4, Ch. 11
    "EF_urea": {
        "value": 0.20, "unit": "t C per t urea",
        "source": "IPCC 2006, Vol.4 Ch.11, Eq. 11.13 default"},
    "EF_limestone": {
        "value": 0.12, "unit": "t C per t limestone (CaCO3)",
        "source": "IPCC 2006, Vol.4 Ch.11, Eq. 11.12 default"},
    # --- Global warming potentials (100-year), IPCC AR6 WG1 (2021) Table 7.15
    "GWP_N2O": {"value": 273, "unit": "kg CO2e per kg N2O", "source": "IPCC AR6 (2021)"},
    # --- Fuel: approximate combustion factor for diesel
    "EF_diesel": {
        "value": 2.68, "unit": "kg CO2 per litre diesel",
        "source": "Approximate tank-to-wheel value (IPCC 2006 Vol.2 default for diesel, "
                  "about 74.1 t CO2/TJ); check national inventory values"},
    # --- Site/product specific: supplied per farm in the input file
    "EF_grid_electricity": {
        "value": None, "unit": "kg CO2e per kWh",
        "source": "USER_INPUT: national grid factor for the year of interest"},
    "EF_n_manufacture": {
        "value": None, "unit": "kg CO2e per kg N produced",
        "source": "USER_INPUT: supplier carbon footprint or LCA database value"},
}

N2O_N_TO_N2O = 44 / 28
C_TO_CO2 = 44 / 12
UREA_N_CONTENT = 0.46


def f(name: str) -> float:
    return FACTORS[name]["value"]
