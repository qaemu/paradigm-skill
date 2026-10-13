#!/usr/bin/env python3
"""PARADIGMA analysis engine.

Subcommands
  cpi     Download US CPI-U (FRED CPIAUCSL), save annual averages to cpi.csv
  curves  Robust cost/performance curves from points.csv (+ constraints.csv, cpi.csv)
  gap     Gap matrix from curves.csv + activity.csv (+ constraints.csv)
  papers  Yearly paper counts from OpenAlex for each query in queries.csv

Run `python3 paradigma.py <cmd> -h` for options. Only pandas, numpy, matplotlib
are required; scipy is used when present.
"""
import argparse
import csv
import io
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd

try:
    from scipy.stats import theilslopes as _theil
except Exception:  # scipy missing
    _theil = None


# ----------------------------------------------------------------- helpers
def theil_sen(x, y):
    """Return slope, intercept, slope_lo, slope_hi (95%)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if _theil is not None:
        s, b, lo, hi = _theil(y, x, 0.95)
        return s, b, lo, hi
    slopes = [(y[j] - y[i]) / (x[j] - x[i])
              for i in range(len(x)) for j in range(i + 1, len(x)) if x[j] != x[i]]
    s = float(np.median(slopes))
    b = float(np.median(y - s * x))
    lo, hi = np.percentile(slopes, [2.5, 97.5])
    return s, b, float(lo), float(hi)


def parse_date(d):
    """'2014' | '2014-Q3' | '2014-07' | '2014-07-15' -> (decimal_year, year, quarter)."""
    d = str(d).strip()
    m = re.fullmatch(r"(\d{4})-?Q([1-4])", d, re.I)
    if m:
        y, q = int(m.group(1)), int(m.group(2))
        return y + (q - 0.5) / 4, y, q
    m = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-(\d{1,2}))?", d)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        return y + (mo - 0.5) / 12, y, (mo - 1) // 3 + 1
    m = re.fullmatch(r"(\d{4})(?:\.0)?", d)
    if m:
        y = int(m.group(1))
        return y + 0.5, y, None
    raise ValueError(f"bad date: {d!r}")


def pct_rank(s, ascending=True):
    s = pd.Series(s, dtype=float)
    r = s.rank(pct=True, ascending=ascending, method="average")
    return r


# --------------------------------------------------------------------- cpi
def cmd_cpi(a):
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
    raw = urllib.request.urlopen(url, timeout=30).read().decode()
    df = pd.read_csv(io.StringIO(raw))
    df.columns = ["date", "cpi"]
    df["cpi"] = pd.to_numeric(df["cpi"], errors="coerce")
    df["year"] = pd.to_datetime(df["date"]).dt.year
    g = df.dropna().groupby("year").agg(cpi=("cpi", "mean"), months=("cpi", "size")).reset_index()
    g["source"] = url
    g.to_csv(a.out, index=False)
    print(f"wrote {a.out}: {g.year.min()}-{g.year.max()} (last year months={int(g.months.iloc[-1])})")


# ------------------------------------------------------------------ curves
def cmd_curves(a):
    pts = pd.read_csv(a.points, dtype=str).fillna("")
    cons = pd.read_csv(a.constraints, dtype=str).fillna("") if os.path.exists(a.constraints) else pd.DataFrame()
    better = dict(zip(cons.get("constraint_id", []), cons.get("better", []))) if len(cons) else {}
    cpi = pd.read_csv(a.cpi) if a.cpi and os.path.exists(a.cpi) else None
    if cpi is not None:
        # a year counts as complete with >=10 monthly readings (e.g. Oct-2025 CPI was never published)
        full = cpi[cpi["months"] >= 10] if "months" in cpi else cpi
        base_year = int(a.base_year or full.year.max())
        cpi_map = dict(zip(cpi.year.astype(int), cpi.cpi.astype(float)))
        base_cpi = cpi_map[base_year]
    else:
        base_year, cpi_map, base_cpi = None, {}, None

    rows, rejects = [], []
    for i, r in pts.iterrows():
        why = None
        try:
            t, y, q = parse_date(r["date"])
            v = float(r["value"])
            if v <= 0:
                why = "value must be > 0 (log scale)"
        except Exception as e:
            why = str(e)
        if not why and r.get("source_url", "").strip() == "":
            why = "missing source_url"
        cur = (r.get("currency", "") or "").upper()
        basis = (r.get("price_basis", "") or "").lower()
        if not why and cur not in ("", "USD", "NA", "N/A"):
            why = f"currency {cur}: convert to USD before analysis"
        if why:
            rejects.append({**r.to_dict(), "reject_reason": why})
            continue
        real = v
        if cur == "USD" and basis.startswith("nominal"):
            if cpi_map.get(y) is None:
                rejects.append({**r.to_dict(), "reject_reason": f"no CPI for {y}"})
                continue
            real = v * base_cpi / cpi_map[y]
        elif cur == "USD" and basis.startswith("real-"):
            ry = int(basis.split("-")[1])
            if cpi_map.get(ry) is not None:
                real = v * base_cpi / cpi_map[ry]
        rows.append({"constraint_id": r["constraint_id"], "tier": r.get("tier", "") or "all",
                     "t": t, "year": y, "quarter": q, "value_real": real,
                     "source_url": r["source_url"].strip()})
    d = pd.DataFrame(rows)
    if rejects:
        pd.DataFrame(rejects).to_csv(os.path.join(a.outdir, "rejected_points.csv"), index=False)
    if d.empty:
        sys.exit("no usable points")

    per_rows, curve_rows = [], []
    for (cid, tier), g in d.groupby(["constraint_id", "tier"]):
        # choose period
        period = a.period
        if period == "auto":
            gq = g.dropna(subset=["quarter"])
            if len(gq) == len(g) and len(g) > 0:
                n_q = gq.groupby(["year", "quarter"]).size()
                period = "quarter" if (n_q >= a.min_n).mean() >= 0.6 and len(n_q) >= 8 else "year"
            else:
                period = "year"
        if period == "quarter":
            g = g.dropna(subset=["quarter"]).copy()
            g["period"] = g.year.astype(str) + "-Q" + g.quarter.astype(int).astype(str)
            g["pt"] = g.year + (g.quarter.astype(float) - 0.5) / 4
        else:
            g = g.copy()
            g["period"] = g.year.astype(str)
            g["pt"] = g.year + 0.5
        agg = g.groupby(["period", "pt"]).agg(
            n=("value_real", "size"), median=("value_real", "median"),
            q1=("value_real", lambda s: s.quantile(.25)), q3=("value_real", lambda s: s.quantile(.75)),
            sources=("source_url", "nunique")).reset_index().sort_values("pt")
        agg["low_confidence"] = agg.n < a.min_n
        # rolling median over 4 quarters to smooth sparse quarterly data
        if period == "quarter":
            agg["rolling4_median"] = agg["median"].rolling(4, min_periods=2).median()
        for _, p in agg.iterrows():
            per_rows.append({"constraint_id": cid, "tier": tier, "period_type": period, **p.to_dict()})

        # fit on period medians (one vote per period); fallback to points
        fit_on = agg if len(agg) >= 4 else g.rename(columns={"t": "pt", "value_real": "median"})
        x = fit_on["pt"].astype(float).values
        yv = np.log10(fit_on["median"].astype(float).values)
        res = {"constraint_id": cid, "tier": tier, "period_type": period,
               "n_points": len(g), "n_periods": len(agg), "n_sources": g.source_url.nunique(),
               "first_period": agg.period.iloc[0], "last_period": agg.period.iloc[-1],
               "low_conf_period_share": round(float(agg.low_confidence.mean()), 2),
               "better": better.get(cid, "lower") or "lower"}
        if len(np.unique(x)) < 3:
            res.update({"fit": "insufficient (<3 distinct periods)", "grade": "D"})
            curve_rows.append(res)
            continue
        s, b, lo, hi = theil_sen(x, yv)
        span = x.max() - x.min()
        fold = 10 ** (s * span)
        res.update({
            "fit": "theil-sen on log10(period medians)" if fit_on is agg else "theil-sen on log10(points)",
            "annual_change_pct": round((10 ** s - 1) * 100, 2),
            "annual_change_ci_low_pct": round((10 ** lo - 1) * 100, 2),
            "annual_change_ci_high_pct": round((10 ** hi - 1) * 100, 2),
            "fitted_start": round(10 ** (b + s * x.min()), 6),
            "fitted_end": round(10 ** (b + s * x.max()), 6),
            "fold_change_over_window": round(fold, 4),
            "span_years": round(span, 2),
        })
        # recent trend (last 5 years of data)
        recent = fit_on[fit_on.pt >= x.max() - 5]
        if recent.pt.nunique() >= 3:
            rs, *_ = theil_sen(recent.pt.astype(float).values, np.log10(recent["median"].astype(float).values))
            res["recent5y_annual_change_pct"] = round((10 ** rs - 1) * 100, 2)
        # improvement direction (positive = getting better)
        sign = -1 if res["better"] == "lower" else 1
        imp_lo, imp_hi = sorted([sign * lo, sign * hi])
        imp = sign * s
        improvement_fold = 10 ** (imp * span)
        res["improvement_fold"] = round(improvement_fold, 3)
        if improvement_fold >= 10:
            cls = "improved >=10x"
        elif imp_lo > 0 and (10 ** imp - 1) >= 0.05:
            cls = "improving"
        elif imp_hi < 0 and (10 ** (-imp) - 1) >= 0.05:
            cls = "worsening (constraint tightening)"
        else:
            cls = "flat / unclear"
        res["class"] = cls
        if "recent5y_annual_change_pct" in res:
            r5 = sign * math.log10(1 + res["recent5y_annual_change_pct"] / 100)
            res["trend_shape"] = ("accelerating" if r5 > imp * 1.25 else
                                  "decelerating" if r5 < imp * 0.75 else "steady")
        ci_w = abs(hi - lo) / max(abs(s), 1e-9)
        if len(agg) >= 8 and res["n_sources"] >= 3 and res["low_conf_period_share"] <= 0.2 and ci_w <= 1:
            grade = "A"
        elif len(agg) >= 5 and res["n_sources"] >= 2:
            grade = "B"
        else:
            grade = "C"
        res["grade"] = grade
        curve_rows.append(res)

    pd.DataFrame(per_rows).to_csv(os.path.join(a.outdir, "periods.csv"), index=False)
    cv = pd.DataFrame(curve_rows)
    cv.to_csv(os.path.join(a.outdir, "curves.csv"), index=False)
    meta = {"base_year": base_year, "min_n": a.min_n, "rejected": len(rejects)}
    json.dump(meta, open(os.path.join(a.outdir, "curves_meta.json"), "w"), indent=2)
    print(cv.to_string(index=False))
    print(f"\nrejected points: {len(rejects)}  base year: {base_year}")
    if a.plots:
        plot_curves(d, pd.DataFrame(per_rows), cv, cons, a.outdir, base_year)


def plot_curves(d, per, cv, cons, outdir, base_year):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = dict(zip(cons.get("constraint_id", []), cons.get("name", []))) if len(cons) else {}
    units = dict(zip(cons.get("constraint_id", []), cons.get("unit", []))) if len(cons) else {}
    os.makedirs(os.path.join(outdir, "plots"), exist_ok=True)
    for (cid, tier), g in d.groupby(["constraint_id", "tier"]):
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter(g.t, g.value_real, s=12, alpha=.4, color="#888", label="data points")
        p = per[(per.constraint_id == cid) & (per.tier == tier)]
        ax.plot(p.pt, p["median"], "o-", color="#2a6", label="period median")
        c = cv[(cv.constraint_id == cid) & (cv.tier == tier)]
        if len(c) and not pd.isna(c.iloc[0].get("fitted_start", np.nan)):
            x0, x1 = p.pt.min(), p.pt.max()
            ax.plot([x0, x1], [c.iloc[0].fitted_start, c.iloc[0].fitted_end], "--", color="#c33",
                    label=f"robust trend {c.iloc[0].annual_change_pct:+.1f}%/yr")
        ax.set_yscale("log")
        from matplotlib.ticker import MaxNLocator
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(f"{names.get(cid, cid)} [{tier}]")
        unit = units.get(cid, "")
        ax.set_ylabel(f"{unit} ({base_year} USD)" if base_year else unit)
        ax.legend(fontsize=8)
        ax.grid(alpha=.3, which="both")
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "plots", f"curve_{cid}_{tier}.png"), dpi=130)
        plt.close(fig)


# --------------------------------------------------------------------- gap
def cmd_gap(a):
    cons = pd.read_csv(a.constraints, dtype=str).fillna("")
    act = pd.read_csv(a.activity)
    cv = pd.read_csv(a.curves) if os.path.exists(a.curves) else pd.DataFrame()
    df = cons[["constraint_id", "name", "family"]].copy()

    # improvement score: measured curves -> log10(improvement_fold) per decade; qualitative 0-3 otherwise
    imp = {}
    if len(cv) and "improvement_fold" in cv:
        best = cv.dropna(subset=["improvement_fold"]).sort_values("n_points", ascending=False)
        best = best.drop_duplicates("constraint_id")
        for _, r in best.iterrows():
            per_decade = math.log10(max(r.improvement_fold, 1e-9)) / max(r.span_years, 1) * 10
            imp[r.constraint_id] = (per_decade, r.get("grade", ""), "measured")
    qual = dict(zip(cons.constraint_id, cons.get("qualitative_change_0to3", [""] * len(cons))))
    vals, grades, kinds = [], [], []
    for cid in df.constraint_id:
        if cid in imp:
            v, gr, k = imp[cid]
        elif str(qual.get(cid, "")).strip() not in ("", "nan"):
            # 0..3 qualitative mapped onto log10-per-decade scale (3 ~ 10x/decade)
            v, gr, k = float(qual[cid]) / 3, "Q", "qualitative"
        else:
            v, gr, k = np.nan, "", "none"
        vals.append(v); grades.append(gr); kinds.append(k)
    df["improvement_log10_per_decade"] = vals
    df["improvement_basis"] = kinds
    df["curve_grade"] = grades
    df = df.merge(act, on="constraint_id", how="left")
    if "threshold_crossed" in df:
        df["threshold_crossed"] = df.threshold_crossed.astype(str).str.lower().isin(["1", "true", "yes", "y"])
    else:
        df["threshold_crossed"] = False

    df["drop_score"] = pct_rank(df.improvement_log10_per_decade)
    df.loc[df.threshold_crossed, "drop_score"] = np.minimum(1, df.loc[df.threshold_crossed, "drop_score"] + 0.15)

    signals = [c for c in ["companies_count", "funding_usd_5y", "patents_last3y", "launches_count", "job_postings"]
               if c in df]
    ranks = [pct_rank(np.log1p(pd.to_numeric(df[c], errors="coerce"))) for c in signals]
    df["activity_score"] = pd.concat(ranks, axis=1).mean(axis=1, skipna=True) if ranks else np.nan
    df["activity_signals_used"] = df[signals].notna().sum(axis=1) if signals else 0

    if "papers_last3y" in df:
        papers = pd.to_numeric(df.papers_last3y, errors="coerce")
        comp = pd.to_numeric(df.get("companies_count", 0), errors="coerce").fillna(0)
        df["research_to_commerce"] = (papers / (comp + 1)).round(1)
        df["research_ahead_score"] = pct_rank(np.log1p(df.research_to_commerce))
    if "papers_prev3y" in df and "papers_last3y" in df:
        df["papers_growth"] = (pd.to_numeric(df.papers_last3y, errors="coerce") /
                               pd.to_numeric(df.papers_prev3y, errors="coerce").replace(0, np.nan)).round(2)

    hi_d = df.drop_score >= a.cut
    hi_a = df.activity_score >= a.cut
    df["quadrant"] = np.select(
        [hi_d & ~hi_a, hi_d & hi_a, ~hi_d & hi_a, ~hi_d & ~hi_a],
        ["WHITE SPACE (fell, few builders)", "CROWDED (fell, many builders)",
         "HYPE RISK (little change, many builders)", "DORMANT"], default="UNSCORED")
    df.loc[df.drop_score.isna() | df.activity_score.isna(), "quadrant"] = "UNSCORED"
    df["gap_score"] = (df.drop_score * (1 - df.activity_score)).round(3)
    if "research_ahead_score" in df:
        df["gap_score"] = (df.gap_score * (0.8 + 0.4 * df.research_ahead_score.fillna(0.5))).round(3)
    df = df.sort_values("gap_score", ascending=False)
    df.to_csv(os.path.join(a.outdir, "gap_matrix.csv"), index=False)
    cols = ["constraint_id", "name", "drop_score", "activity_score", "gap_score", "quadrant"]
    print(df[[c for c in cols if c in df]].to_string(index=False))

    if a.plots:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        s = df.dropna(subset=["drop_score", "activity_score"])
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.axvline(a.cut, color="#bbb", lw=1); ax.axhline(a.cut, color="#bbb", lw=1)
        ax.scatter(s.activity_score, s.drop_score, s=60, color="#2a6")
        for _, r in s.iterrows():
            ax.annotate(r["name"][:28], (r.activity_score, r.drop_score), fontsize=7,
                        xytext=(4, 3), textcoords="offset points")
        ax.text(0.02, 0.98, "WHITE SPACE", transform=ax.transAxes, va="top", fontsize=9, color="#2a6")
        ax.text(0.98, 0.98, "CROWDED", transform=ax.transAxes, va="top", ha="right", fontsize=9, color="#777")
        ax.text(0.98, 0.02, "HYPE RISK", transform=ax.transAxes, ha="right", fontsize=9, color="#c33")
        ax.text(0.02, 0.02, "DORMANT", transform=ax.transAxes, fontsize=9, color="#777")
        ax.set_xlabel("Activity score (percentile: companies, funding, patents, launches)")
        ax.set_ylabel("Drop score (percentile: how much the constraint fell)")
        ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
        ax.set_title("PARADIGMA gap matrix")
        fig.tight_layout()
        os.makedirs(os.path.join(a.outdir, "plots"), exist_ok=True)
        fig.savefig(os.path.join(a.outdir, "plots", "gap_matrix.png"), dpi=140)
        plt.close(fig)


# ------------------------------------------------------------------ papers
def cmd_papers(a):
    q = pd.read_csv(a.queries, dtype=str)
    key = os.environ.get("OPENALEX_API_KEY", "")
    out = []
    for _, r in q.iterrows():
        params = {"filter": f"title_and_abstract.search:{r['query']},publication_year:{a.start}-{a.end}",
                  "group_by": "publication_year"}
        if key:
            params["api_key"] = key
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        try:
            js = json.loads(urllib.request.urlopen(url, timeout=30).read().decode())
            for gr in js.get("group_by", []):
                out.append({"constraint_id": r["constraint_id"], "query": r["query"],
                            "year": int(gr["key"]), "papers": int(gr["count"]),
                            "source_url": url.split("&api_key")[0]})
            print(f"ok   {r['constraint_id']}: {r['query']}")
        except Exception as e:
            body = getattr(e, "read", lambda: b"")().decode(errors="ignore")[:160]
            print(f"FAIL {r['constraint_id']}: {e} {body}")
    if not out:
        sys.exit("no OpenAlex data (set OPENALEX_API_KEY or use the web fallback)")
    df = pd.DataFrame(out)
    df.to_csv(a.out, index=False)
    last = a.end
    l3 = df[df.year.between(last - 2, last)].groupby("constraint_id").papers.sum().rename("papers_last3y")
    p3 = df[df.year.between(last - 5, last - 3)].groupby("constraint_id").papers.sum().rename("papers_prev3y")
    summ = pd.concat([l3, p3], axis=1).fillna(0).astype(int)
    summ.to_csv(os.path.splitext(a.out)[0] + "_summary.csv")
    print(summ.to_string())


# -------------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description="PARADIGMA analysis engine")
    sp = p.add_subparsers(dest="cmd", required=True)

    c = sp.add_parser("cpi"); c.add_argument("--out", default="cpi.csv"); c.set_defaults(f=cmd_cpi)

    c = sp.add_parser("curves")
    c.add_argument("--points", default="points.csv")
    c.add_argument("--constraints", default="constraints.csv")
    c.add_argument("--cpi", default="cpi.csv")
    c.add_argument("--base-year", type=int)
    c.add_argument("--period", choices=["auto", "year", "quarter"], default="auto")
    c.add_argument("--min-n", type=int, default=3)
    c.add_argument("--outdir", default=".")
    c.add_argument("--plots", action="store_true")
    c.set_defaults(f=cmd_curves)

    c = sp.add_parser("gap")
    c.add_argument("--constraints", default="constraints.csv")
    c.add_argument("--curves", default="curves.csv")
    c.add_argument("--activity", default="activity.csv")
    c.add_argument("--cut", type=float, default=0.5)
    c.add_argument("--outdir", default=".")
    c.add_argument("--plots", action="store_true")
    c.set_defaults(f=cmd_gap)

    c = sp.add_parser("papers")
    c.add_argument("--queries", default="paper_queries.csv")
    c.add_argument("--start", type=int, default=2005)
    c.add_argument("--end", type=int, default=2025)
    c.add_argument("--out", default="papers.csv")
    c.set_defaults(f=cmd_papers)

    a = p.parse_args()
    if hasattr(a, "outdir"):
        os.makedirs(a.outdir, exist_ok=True)
    a.f(a)


if __name__ == "__main__":
    main()
