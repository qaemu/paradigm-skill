#!/usr/bin/env python3
"""Offline test of the PARADIGMA engine on synthetic data with known answers.

    python3 tests/test_engine.py

Builds a fixture with a known -20%/yr cost curve (plus a 100x outlier), a known
+30%/yr performance curve with quarterly data, a flat sparse series, a series with
only 3 periods, and two bad rows that must be rejected. Also reruns the curves on a
10-year window to check that points outside it are left out of the curves but kept in out_of_window.csv. Uses a flat CPI so the expected trends are exact.
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

ENGINE = os.path.join(os.path.dirname(__file__), "..", "skills", "paradigma", "scripts", "paradigma.py")


def fixture(d):
    rng = np.random.default_rng(1)
    rows = []
    for y in range(2006, 2026):
        for k in range(rng.integers(1, 5)):
            rows.append(dict(constraint_id="C1", tier="industrial", date=str(y),
                             value=10000 * 0.8 ** (y - 2006) * rng.lognormal(0, 0.15), unit="USD/unit",
                             currency="USD", price_basis="nominal", source_url=f"https://example.com/c1/{y}/{k}"))
    rows.append(dict(constraint_id="C1", tier="industrial", date="2015", value=900000, unit="USD/unit",
                     currency="USD", price_basis="nominal", source_url="https://example.com/outlier"))
    for y in range(2018, 2026):
        for q in range(1, 5):
            for k in range(4):
                rows.append(dict(constraint_id="C2", tier="all", date=f"{y}-Q{q}",
                                 value=100 * 1.3 ** ((y - 2018) + (q - 1) / 4) * rng.lognormal(0, 0.1),
                                 unit="Wh/kg", currency="", price_basis="",
                                 source_url=f"https://example.com/c2/{y}{q}{k}"))
    for y in (2010, 2015, 2020, 2024):
        rows.append(dict(constraint_id="C3", tier="all", date=str(y), value=50 * rng.lognormal(0, 0.05),
                         unit="USD/h", currency="USD", price_basis="nominal", source_url=f"https://example.com/c3/{y}"))
    for y, val in ((2016, 80), (2016, 82), (2019, 60), (2022, 45)):            # 3 periods: fit falls back to points
        rows.append(dict(constraint_id="C5", tier="all", date=str(y), value=val, unit="USD/unit", currency="USD",
                         price_basis="nominal", source_url=f"https://example.com/c5/{y}/{val}"))
    rows.append(dict(constraint_id="C3", tier="all", date="2012", value=40, unit="USD/h", currency="USD",
                     price_basis="nominal", source_url=""))                       # no source -> reject
    rows.append(dict(constraint_id="C3", tier="all", date="2013", value=40, unit="ARS/h", currency="ARS",
                     price_basis="nominal", source_url="https://example.com/ars"))  # non-USD -> reject
    pd.DataFrame(rows).to_csv(os.path.join(d, "points.csv"), index=False)
    pd.DataFrame([
        dict(constraint_id="C1", name="Industrial sensor", family="cost", unit="USD/unit", better="lower", qualitative_change_0to3=""),
        dict(constraint_id="C2", name="Energy density", family="performance", unit="Wh/kg", better="higher", qualitative_change_0to3=""),
        dict(constraint_id="C3", name="Technician labor", family="skill", unit="USD/h", better="lower", qualitative_change_0to3=""),
        dict(constraint_id="C5", name="Sparse series", family="cost", unit="USD/unit", better="lower", qualitative_change_0to3=""),
        dict(constraint_id="C6", name="Export controls", family="supply", unit="", better="", qualitative_change_0to3="2", direction="tightening"),
        dict(constraint_id="C4", name="Drone rule", family="legal", unit="", better="", qualitative_change_0to3="3"),
    ]).to_csv(os.path.join(d, "constraints.csv"), index=False)
    pd.DataFrame([
        dict(constraint_id="C1", companies_count=40, funding_usd_5y=8e8, patents_last3y=300, launches_count=25, papers_last3y=900, papers_prev3y=600, threshold_crossed="yes"),
        dict(constraint_id="C2", companies_count=3, funding_usd_5y=2e7, patents_last3y=40, launches_count=2, papers_last3y=2500, papers_prev3y=1200, threshold_crossed="no"),
        dict(constraint_id="C3", companies_count=10, funding_usd_5y=5e7, patents_last3y=5, launches_count=4, papers_last3y=50, papers_prev3y=45, threshold_crossed="no"),
        dict(constraint_id="C6", companies_count=2, funding_usd_5y=1e6, patents_last3y=1, launches_count=1, papers_last3y=20, papers_prev3y=20, threshold_crossed="no"),
        dict(constraint_id="C4", companies_count=1, funding_usd_5y=1e6, patents_last3y=10, launches_count=1, papers_last3y=300, papers_prev3y=100, threshold_crossed="yes"),
    ]).to_csv(os.path.join(d, "activity.csv"), index=False)
    pd.DataFrame({"year": range(2000, 2027), "cpi": 100.0, "months": 12}).to_csv(os.path.join(d, "cpi.csv"), index=False)


def run(d, *args):
    subprocess.run([sys.executable, ENGINE, *args], cwd=d, check=True, capture_output=True)


def main():
    with tempfile.TemporaryDirectory() as d:
        fixture(d)
        run(d, "curves", "--plots")
        run(d, "gap", "--plots")
        pd.DataFrame([dict(finding="Sensor cost fell", constraint_ids="C1", number="-20%/yr", confidence="B", meaning="test")]).to_csv(
            os.path.join(d, "findings.csv"), index=False)
        has_xl = True
        try:
            import openpyxl  # noqa: F401
            run(d, "workbook", "--field", "test field", "--start", "2006", "--end", "2025", "--out", "wb.xlsx")
            sheets = openpyxl.load_workbook(os.path.join(d, "wb.xlsx")).sheetnames
        except ImportError:
            has_xl, sheets = False, []
        run(d, "curves", "--start", "2012", "--end", "2021", "--outdir", "w10")
        cw = pd.read_csv(os.path.join(d, "w10", "curves.csv")).set_index("constraint_id")
        ow = pd.read_csv(os.path.join(d, "w10", "out_of_window.csv"))
        rw_path = os.path.join(d, "w10", "rejected_points.csv")
        rw = pd.read_csv(rw_path) if os.path.exists(rw_path) else pd.DataFrame(columns=["reject_reason"])
        cv = pd.read_csv(os.path.join(d, "curves.csv")).set_index("constraint_id")
        rej = pd.read_csv(os.path.join(d, "rejected_points.csv"))
        gm = pd.read_csv(os.path.join(d, "gap_matrix.csv")).set_index("constraint_id")
        checks = {
            "C1 trend ~ -20%/yr despite a 100x outlier": -23 < cv.loc["C1", "annual_change_pct"] < -17,
            "C1 classed as improved >=10x": cv.loc["C1", "class"] == "improved >=10x",
            "C2 detected as quarterly": cv.loc["C2", "period_type"] == "quarter",
            "C2 trend ~ +30%/yr": 27 < cv.loc["C2", "annual_change_pct"] < 33,
            "C3 flat and graded C": cv.loc["C3", "class"] == "flat / unclear" and cv.loc["C3", "grade"] == "C",
            "2 bad rows rejected": len(rej) == 2,
            "C4 (rule removed, few builders) lands in open gap": gm.loc["C4", "quadrant"].startswith("OPEN GAP"),
            "C2 ranks above C1 on gap score": gm.loc["C2", "gap_score"] > gm.loc["C1", "gap_score"],
            "C1 lands in crowded": gm.loc["C1", "quadrant"].startswith("CROWDED"),
            "C5 with 3 periods still gets a trend": cv.loc["C5", "annual_change_pct"] < 0,
            "10-year window keeps C1 inside 2012-2021": int(str(cw.loc["C1", "first_period"])[:4]) >= 2012 and int(str(cw.loc["C1", "last_period"])[:4]) <= 2021,
            "points outside the window are kept in out_of_window.csv, not rejected":
                len(ow) > 0 and ow.window_note.str.startswith("outside window").all()
                and not rw.reject_reason.astype(str).str.startswith("outside window").any(),
            "bad rows are still rejected in the windowed run": len(rw) == 2,
            "tightening constraint kept off the matrix": gm.loc["C6", "quadrant"] == "NOT PLACED",
            "workbook opens on Start here, then Key findings": (not has_xl) or sheets[:2] == ["Start here", "Key findings"],
            "plots written": os.path.exists(os.path.join(d, "plots", "gap_matrix.png")),
        }
    for name, ok in checks.items():
        print(("PASS " if ok else "FAIL ") + name)
    sys.exit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
