#!/usr/bin/env python3
"""Merge raw agent files into the PARADIGMA input CSVs (companies, noncost, constraints, activity)."""
import glob, re
import numpy as np, pandas as pd

def load(pattern, **kw):
    fs = sorted(glob.glob(pattern))
    return pd.concat([pd.read_csv(f, dtype=str, **kw).assign(_file=f.split("/")[-1]) for f in fs], ignore_index=True).fillna("") if fs else pd.DataFrame()

# ---- companies
co = load("raw/companies_*.csv")
co["company_key"] = co.company.str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
co = co.drop_duplicates(["company_key", "constraint_id"])
co = co[co.constraint_id.str.match(r"C\d\d$")]
cols = ["company","constraint_id","what_they_do","founded","last_funding_usd","last_funding_date","funding_source_url",
        "status","status_evidence_url","consensus","country","note","_file"]
co[[c for c in cols if c in co]].to_csv("companies.csv", index=False)

fe = load("raw/funding_events_*.csv")
fe["company_key"] = fe.company.str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
fe["amount"] = pd.to_numeric(fe.amount_usd.str.replace(",", ""), errors="coerce")
fe = fe.drop_duplicates(["company_key", "date", "amount"])
# round-level dedupe (verification found the same round logged from several sources with different dates/amounts):
# keep one row per company+round label, the one with the smallest disclosed amount (conservative)
fe["round_key"] = fe["round"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
fe["_amt"] = fe["amount"].fillna(1e18)
fe = fe.sort_values("_amt")
has_round = fe.round_key != ""
fe = pd.concat([fe[has_round].drop_duplicates(["company_key", "round_key"]), fe[~has_round]]).sort_values(["company_key", "date"])
fe = fe.drop(columns=["round_key", "_amt"])
fe.drop(columns=["company_key", "amount"]).to_csv("funding_events.csv", index=False)

la = load("raw/launches_*.csv")
la["company_key"] = la.company.str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
la = la.drop_duplicates(["constraint_id", "company_key", "product"])
la.to_csv("launches.csv", index=False)

# ---- noncost
nc = load("raw/noncost_*.csv")
nc.drop(columns="_file").to_csv("noncost.csv", index=False)

# ---- constraints: qualitative scores
cons = pd.read_csv("constraints.csv", dtype=str).fillna("")
q = load("raw/qual_*.csv")
for c in ["direction_note", "tightening_score_0to3"]:
    if c not in cons: cons[c] = ""
for _, r in q.iterrows():
    m = cons.constraint_id == r.constraint_id
    cons.loc[m, "qualitative_justification"] = r.qualitative_justification
    cons.loc[m, "direction_note"] = r.direction
    if r.direction == "loosening":
        cons.loc[m, "qualitative_change_0to3"] = r.qualitative_change_0to3
    else:
        cons.loc[m, "tightening_score_0to3"] = r.qualitative_change_0to3
# manual, evidence-based entries (labor): see report
m = cons.constraint_id == "C10"
cons.loc[m, "direction_note"] = "tightening"
cons.loc[m, "tightening_score_0to3"] = "1"
cons.loc[m, "qualitative_justification"] = ("Weak tightening. Deloitte/Manufacturing Institute project 1.9M unfilled manufacturing jobs by 2033 (2024 study; 2.4M by 2028 in the 2018 study), "
    "but those are manufacturing-wide. For industrial machinery mechanics (49-9041), BLS employment rose from 250,810 (2006) to 412,650 (2023) while the real median wage "
    "was flat (+0.2%/yr, C09). Shortage claims are not visible in the wage data. Sources: labor_facts_D.csv, points.csv C09.")
cons.loc[cons.constraint_id.isin(["C08"]), "direction_note"] = "pressure (measured)"
cons.loc[cons.constraint_id.isin(["C09"]), "direction_note"] = "pressure (measured)"
cons.loc[cons.constraint_id.isin(["C01","C02","C04","C06"]), "direction_note"] = "loosening (measured)"
cons.loc[cons.constraint_id.isin(["C03","C05","C07"]), "direction_note"] = "unmeasured (data gap)"
cons.to_csv("constraints.csv", index=False)
# gap pool: leave out pressure / tightening / mixed / unmeasured-without-score constraints
REVIEW_EXCLUDE = {"C04": "curve invalid after why-not review: mixes vendors and pixel counts; one-time step in 2014, flat since"}
cons.loc[cons.constraint_id.isin(REVIEW_EXCLUDE), "direction_note"] = "measured, excluded after review"
cons.to_csv("constraints.csv", index=False)
pool = cons[~cons.direction_note.str.contains("pressure|tightening|mixed|unmeasured|excluded")]
pool.to_csv("constraints_gap.csv", index=False)

# ---- activity
rows = []
fe["date_ok"] = fe.date >= "2021-10-01"
for cid in cons.constraint_id:
    sub = co[co.constraint_id == cid]
    if sub.empty:
        rows.append({"constraint_id": cid, "notes": "no attributable company found in scan (unknown, not zero)"}); continue
    keys = set(sub.company_key)
    f = fe[fe.company_key.isin(keys) & fe.date_ok]
    funding = f.amount.sum() if f.amount.notna().any() else np.nan
    l = la[(la.constraint_id == cid) & (la.get("date", "") >= "2021-01-01")] if len(la) else la
    fy = pd.to_numeric(sub.founded.str[:4], errors="coerce")
    startups = sub[fy >= 2012].company_key.nunique()
    rows.append({"constraint_id": cid, "companies_count": len(keys), "funding_usd_5y": funding,
                 "launches_count": len(l) if len(l) else np.nan,
                 "notes": f"{startups} founded 2012+; {int((sub.consensus=='yes').sum())} consensus; "
                          f"statuses: " + ", ".join(f"{k}={v}" for k, v in sub.status.value_counts().items())})
act = pd.DataFrame(rows)
for c in ["patents_last3y","papers_last3y","papers_prev3y","job_postings","threshold_crossed","patent_query"]:
    act[c] = np.nan
import os
if os.path.exists("papers_summary.csv"):
    ps = pd.read_csv("papers_summary.csv")
    act = act.drop(columns=["papers_last3y", "papers_prev3y"]).merge(ps, on="constraint_id", how="left")
act.to_csv("activity.csv", index=False)
print(act[["constraint_id","companies_count","funding_usd_5y","launches_count","notes"]].to_string(index=False))

# ---- failures, absence, prices
for name in ["failures", "absence"]:
    d = load(f"raw/{name}_*.csv")
    if len(d): d.to_csv(f"{name}.csv", index=False)

wn = load("raw/whynot_*.csv")
wn.drop(columns="_file").to_csv("whynot.csv", index=False)
print(len(wn), "whynot rows")
