---
name: paradigma
license: MIT
description: PARADIGMA maps which constraints (costs, performance, laws, patents, skills, norms, supply) in a given field fell, are falling or are tightening over a chosen number of years (20 by default), who is building on each, and where the white space is. Use when the user calls PARADIGMA or asks for a constraint-shift / paradigm panorama of a field.
---

# PARADIGMA: constraint-shift panorama of a field

**Goal:** give the user a clear, sourced panorama of a field. It covers which constraints fell, are falling or are tightening; who is building on each one; and where constraints fell but few people are building (white space). It is a map for deciding where to act. It is not idea generation and not a list of workarounds.

**Invocation:** `/paradigma <field> [region] [years] [standard|deep]`. The field is required and comes from the invocation. Everything else is optional and can come in any order after the field.

- **`years`**: how many years back the analysis looks. Accept a bare number (`10`), `10y`, `10 years` or `years=10`. Default **20**. Allowed range **5 to 50**; outside it, clamp and say so. An explicit range such as `2010-2025` is also accepted and sets both ends.
- Examples: `/paradigma "solar inverters"`, `/paradigma "dental aligners" EU 10`, `/paradigma "cargo drones" global 15y deep`, `/paradigma "industrial robots" 2000-2025`.

## Non-negotiable rules

1. **No source, no number.** Every data point, funding figure, date and company claim has a source URL. Never fill a cell from memory or estimate a missing value. Report missing data as missing.
2. **All curve math runs in the script** (Appendix A), never in prose. Use period medians and a robust trend (Theil–Sen on log scale). Never report an endpoint-to-endpoint percentage as a trend.
3. **Mark every company's status** as `announced` | `deployed` | `paying`, with evidence. A press release or a funding round is not traction.
4. **Every white-space candidate gets a "why not" check** before it's reported as white space.
5. **Verify independently before delivery.** An agent that did not do the research checks the numbers and claims.
6. **Be honest about confidence.** Show curve grades (A/B/C/D) and data gaps, and label what is consensus (widely covered) separately from what is non-obvious.
7. **Anchor dates to today.** Get today's date first (time tool or `date`). The analysis window is the `years` ending at the last full calendar year: `END` = last full calendar year, `START` = `END − years + 1`. With the default of 20 and today in 2026, that is 2006–2025. Use `START` and `END` everywhere a window is mentioned below, and print them at the top of the report.

## Inputs and scope

- **Field (required).** If it's missing, ask for it in one question.
- **Breadth check.** If the field is broad (for example "mechanics," "hardware," "health," "energy"), ask once with AskUserQuestion. Offer 3–4 concrete subfields plus "Run broad anyway (shallower)." If nobody answers (unattended run), run broad, cap it at 25 constraints, and say so at the top of the report.
- **Region:** default global. Note where the data is US- or EU-centric.
- **Window (`years`):** see Invocation. Pick it to match how fast the field moves: 5–10 years for software-heavy or fast fields, 20 for most hardware fields, 30–50 for slow infrastructure. Short windows have consequences: with fewer than 8 yearly periods a curve cannot reach grade A unless the data is quarterly, and with 7 years or fewer the trend shape (recent 5 years vs the whole window) is not meaningful, so report it as n/a. Long windows reach back before most online price data; expect more gaps before about 2000.
- **Depth:** `standard` covers 12–25 constraints. `deep` covers up to 40, with more points per curve and why-not checks on all candidates.

## Setup

1. Create a task list with phases 1–7.
2. Make a working folder `paradigma_<field-slug>_<YYYY-MM-DD>/` and copy the analysis engine into it (see Appendix A for where to find it). Then run `python3 paradigma.py cpi`. This downloads US CPI from FRED for the inflation adjustment.
3. Create the CSVs using the schemas in Appendix B: `constraints.csv`, `points.csv`, `activity.csv`, `companies.csv`, `noncost.csv`, `whynot.csv`.

## Phase 1: Break the field into constraints

Ask what it takes to deliver this field's output, and list the inputs in each of these groups:

- components and hardware (sensors, actuators, motors, compute, materials, energy storage)
- manufacturing processes
- software and AI capabilities
- data
- labor and skills
- distribution and channels
- compliance, certification and insurance
- trust

Then run a **PESTEL** sweep (Political, Economic, Social, Technological, Environmental, Legal) for non-cost constraints. Before finalizing, search for constraints specific to the field: "<field> cost reduction," "<field> enabling technologies," "<field> regulation change," and industry-association outlook reports.

For each constraint, record:

- `family`: cost | performance | legal | patent | skill | norm | supply | economic
- a **metric expressed per unit of performance** where possible ($/kWh, $ per sensor channel, $/kg payload, $/hour, Wh/kg)
- `better`: lower or higher
- a one-line note on why it matters to the field

Keep industrial and consumer grades as separate tiers.

## Phase 2: Cost and performance curves

**Run research in parallel.** If an Agent tool is available, split the measured constraints across 3–5 research agents (general-purpose) using the Appendix C prompt. Each agent returns `points.csv` rows only. Merge them yourself.

**Source priority** (record it in `source_type`):

1. **Primary datasets:** Our World in Data, the Santa Fe Institute Performance Curve Database (pcdb.santafe.edu), BloombergNEF public summaries, IEA, NREL, USGS Mineral Commodity Summaries, BLS producer price indices or FRED, and academic learning-curve papers.
2. **Price lists:** manufacturer and distributor price lists (current prices, plus Wayback Machine snapshots for history), teardown reports, and launch press releases with list prices.
3. **Secondary:** public summaries of industry reports and reputable press.

**Data rules:**

- Record the value exactly as published, with its currency, its basis (`nominal`, or `real-YYYY` if it's already inflation-adjusted) and its date precision (YYYY, YYYY-Qn or YYYY-MM).
- For non-USD values, convert using a cited exchange rate for that date and put the rate and source in `note`. If you can't cite a rate, leave the point out. The script rejects non-USD rows.
- Don't mix tiers or product generations in one series.
- **Targets per curve:** at least 3 points per period, at least 5 periods, and at least 2 independent sources. Report shortfalls; don't hide them.

**Run the analysis:**

```
python3 paradigma.py curves --start <START> --end <END> --plots
```

- Choose annual vs quarterly with `--period auto`. Quarterly is used only when the data is dense.
- Check `rejected_points.csv` and fix or drop those rows.
- Look at every plot. If a curve mixes tiers or generations, split it and run again.

**Thresholds.** For each improving constraint, ask: what became viable at today's level, and what becomes viable at the next 10x? Back each answer with a cited first product or deployment that the threshold enabled. Record `threshold_crossed` in `activity.csv` and `threshold_note` in `constraints.csv`.

## Phase 3: Non-cost constraints (PESTEL sweep)

Record each finding in `noncost.csv`. Then give each non-cost constraint a `qualitative_change_0to3` with a justification:

- **0** = no change
- **1** = minor
- **2** = significant
- **3** = a hard barrier was removed (or added, for tightening)

Where to look, by type:

- **Legal and regulatory:**
  - Official gazettes: US Federal Register, EUR-Lex, and national gazettes such as Argentina's Boletín Oficial.
  - Regulator websites, and new or revised standards from ISO, IEC, ASTM, SAE and IEEE.
  - Regulatory sandboxes.
  - **Always capture laws with future effective dates.** They go in the timeline.
- **Patents:**
  - Google Patents or Lens.org: highly cited patents in the field filed 17–20 years before today (this follows the 20-year patent term, not the analysis window), which are expiring now or soon. Also notable patents allowed to lapse early.
  - Record the number, assignee and estimated expiry (filing date + 20 years, marked approximate because patent terms can be adjusted).
- **Skills and labor:**
  - Wage and shortage statistics: BLS Occupational Outlook, OECD and national statistics.
  - Hiring and shortage reports.
  - Rising wages or chronic shortages mean the constraint is **tightening**, which creates pressure to automate.
- **Social norms and behavior:**
  - Pew, Eurobarometer and industry surveys.
  - Google Trends, as cited in articles.
  - Insurers' coverage decisions.
  - Adoption statistics.
- **Supply chain and geopolitics:**
  - Export controls, tariffs and USGS critical-minerals data. These are often tightening.
- **Economic:**
  - Subsidy and incentive programs, and the availability of capital for the field.

## Phase 4: Activity scan (who is building on each constraint)

Use the **same query wording across all constraints** so the signals are comparable. Run in parallel when possible. The activity window is the last 5 years, or the whole analysis window if that is shorter.

- **`companies_count`:** companies founded or pivoted to exploit this constraint after it fell. Record each one in `companies.csv`: what they do, when founded, last disclosed funding (amount, date, source), status (announced, deployed or paying) with an evidence URL, and `consensus`. Set `consensus=yes` if the company is heavily covered or well funded.
- **`funding_usd_5y`:** sum of disclosed funding. Sources include press releases, free Crunchbase and Dealroom pages, and tech press. Note any undisclosed rounds.
- **`patents_last3y`:** result counts from a fixed Google Patents or Lens.org query. Record the query.
- **`papers_last3y` and `papers_prev3y`:**
  - Write `paper_queries.csv` (columns constraint_id, query), then run `python3 paradigma.py papers --start <max(START, END−5)> --end <END>`. The script compares the last 3 years with the 3 before them. This uses OpenAlex, which needs `OPENALEX_API_KEY` in the environment once the free shared quota runs out. Keys are free at openalex.org.
  - If it fails, try WebFetch on the same OpenAlex API URL.
  - If that also fails, leave the papers columns blank (the script handles missing signals) and say so in the report.
- **`launches_count`:** product launches or deployments. `job_postings` is optional.

## Phase 5: Gap matrix and "why not" check

Run:

```
python3 paradigma.py gap --plots
```

The script assigns each constraint to a quadrant:

- **WHITE SPACE:** the constraint fell and few companies are building on it.
- **CROWDED:** it fell and many companies are building on it.
- **HYPE RISK:** little has changed, but many companies are building anyway.
- **DORMANT:** little change and little activity.

A high `research_to_commerce` value means the research is ahead of the companies. That's often the strongest signal.

**Why-not check.** Run it on every WHITE SPACE item and on the top 5 by `gap_score`.

1. Search for failed attempts: Failory, CB Insights post-mortems, "<topic> startup shut down," "<topic> failed," "<topic> pivot."
2. Search for blockers that remain: certification, liability, distribution, unit economics, customer behavior, or another constraint still in place.
3. Give each item one label, with sources, in `whynot.csv`:
   - **UNTRIED:** nobody has seriously built on it.
   - **TRIED TOO EARLY:** a named company failed before the constraint fell. Give dates.
   - **BLOCKED:** name the blocker and whether it's falling.

Only UNTRIED and TRIED TOO EARLY are presented as white space. BLOCKED items go to a **watch list** together with the blocker to monitor. Flag HYPE RISK items explicitly.

## Phase 6: Independent verification

1. Start a **fresh** general-purpose agent that did not do any of the research. Give it only the CSVs.
2. Tell it to open every source URL and confirm that each value, date and claim matches. It should check:
   - every point behind an A- or B-grade curve (or a random sample of at least 40 if there are more than 150)
   - every company claim and funding figure that appears in the summary
   - every non-cost item
3. It returns a mismatch CSV.
4. Fix or drop the mismatched rows, then run `curves` and `gap` again.
5. Report the verification pass rate.

If no Agent tool is available, do this as a separate pass yourself and state in the report that it was self-checked.

## Phase 7: Deliverables

**1. Report.** Use the document artifact type if this session lists one. Otherwise publish an HTML page, or write .md if the user asks for that. Sections in this order:

1. **Panorama** (one page): field, region, window (`START–END`, `years`), date.
   - Top constraints that fell, with fold change and grade.
   - Top tightening constraints.
   - White space (UNTRIED and TRIED TOO EARLY).
   - Crowded zones.
   - Hype risks.
   - **Dated changes coming in the next 1–5 years:** laws taking effect, patents expiring.
2. **Gap matrix** chart.
3. **Constraint cards**, one per constraint:
   - definition
   - curve chart
   - robust yearly change with its 95% confidence interval
   - fold change over the window, trend shape (accelerating / steady / decelerating) and grade
   - thresholds
   - who is building, with status
   - why-not label
4. **Non-cost timeline**, past and upcoming.
5. **Company map:** status and whether it's consensus or non-obvious.
6. **Method and confidence:**
   - data coverage and rejected points
   - verification pass rate
   - regional bias of the sources
   - what paid databases (PitchBook, Gartner and so on) would add
7. **Sources.**

**2. Data workbook.** Use the spreadsheet artifact type if listed, otherwise .xlsx. Sheets: constraints, points, periods, curves, noncost, companies, activity, gap_matrix, whynot, verification.

**3. Final reply:** 3–5 lines covering the biggest shifts, the top white spaces, the main confidence caveat, and the deliverables.

## Interpretation rules for the report

- **Panorama, not prophecy.** Say where the timing is uncertain. Being too early looks the same as being wrong.
- **Flag "early" falls.** If a constraint fell less than 3 years ago, mark it "early."
- **Separate speculation from adoption.** Treat activity driven by speculation or hype differently from real users with a need.
- **Grade C or D curves can't support headline claims.**
- **Don't promote a company from consensus to non-obvious** just because it's small. Base the label on how much coverage it has.

## Appendix A: the analysis engine

The engine is `scripts/paradigma.py`, bundled next to this SKILL.md. Copy it into the working folder, trying these in order:

1. `cp "${CLAUDE_SKILL_DIR}/scripts/paradigma.py" .` (Claude Code sets `CLAUDE_SKILL_DIR`).
2. Copy it from the `scripts/` folder beside this SKILL.md, wherever the host installed the skill.
3. If the host loaded only SKILL.md, download it:
   `curl -fsSL https://raw.githubusercontent.com/qaemu/paradigma-skill/main/skills/paradigma/scripts/paradigma.py -o paradigma.py`

Never rewrite the engine from memory. If none of these work, stop and tell the user the engine is missing.

Subcommands: `cpi`, `curves`, `gap`, `papers`. Run `python3 paradigma.py <cmd> -h` for options. It requires pandas, numpy and matplotlib, and uses scipy if present.

## Appendix B: CSV schemas

**constraints.csv**
`constraint_id,name,family,unit,better,tier_note,why_it_matters,qualitative_change_0to3,qualitative_justification,threshold_note`
- `better`: `lower` or `higher` (measured constraints only).
- `qualitative_change_0to3`: filled for non-cost constraints, or for any constraint without a measurable curve. Leave it blank for measured ones.

**points.csv** (one row per published data point)
`constraint_id,tier,date,value,unit,currency,price_basis,source_url,source_title,source_type,note`
- `date`: `YYYY`, `YYYY-Qn`, `YYYY-MM` or `YYYY-MM-DD`.
- `value`: a number greater than 0.
- `currency`: `USD`, or blank for non-money metrics.
- `price_basis`: `nominal` or `real-YYYY` (blank for non-money metrics).
- `source_type`: `primary` | `pricelist` | `secondary`.

**activity.csv** (one row per constraint; leave unknown values blank, never 0)
`constraint_id,companies_count,funding_usd_5y,patents_last3y,papers_last3y,papers_prev3y,launches_count,job_postings,threshold_crossed,patent_query,notes`

**companies.csv**
`company,constraint_id,what_they_do,founded,last_funding_usd,last_funding_date,funding_source_url,status,status_evidence_url,consensus,country`
- `status`: `announced` | `deployed` | `paying`.
- `consensus`: `yes` | `no`.

**noncost.csv**
`item_id,constraint_id,family,change,direction,jurisdiction,status,date_effective,source_url,note`
- `direction`: `loosening` | `tightening`.
- `status`: `enacted` | `proposed` | `expired` | `expiring`.

**whynot.csv**
`constraint_id,label,failed_attempts,blockers,blocker_trend,source_urls,note`
- `label`: `UNTRIED` | `TRIED TOO EARLY` | `BLOCKED`.

**paper_queries.csv**
`constraint_id,query`

**Script outputs:**
- `curves.csv`: robust yearly change, 95% confidence interval, fold change, class, trend shape, grade
- `periods.csv`: median, n and interquartile range per period, with a low-confidence flag when n < 3
- `rejected_points.csv`
- `gap_matrix.csv`
- `papers.csv` and `papers_summary.csv`
- `plots/*.png`

**Curve grades:**
- **A:** at least 8 periods, at least 3 sources, at most 20% low-n periods, and a tight confidence interval.
- **B:** at least 5 periods and at least 2 sources.
- **C:** usable, but weak.
- **D:** fewer than 3 periods. No trend is computed.

## Appendix C: research agent prompt template (Phase 2 and Phase 4)

> You are collecting sourced data for a market panorama of **<FIELD>** (<REGION>, window <START>–<END>). Today is <DATE>.
> Your constraints: <list of constraint_id, name, metric/unit, tier>.
> Return ONLY CSV rows matching this header: <header from Appendix B>.
> Rules:
> - Every row needs a working source URL that you actually opened. Never estimate or recall numbers from memory. If you can't find data for a period, leave that period out.
> - Record values exactly as published, with currency, nominal or real basis, and date precision. Keep industrial and consumer tiers separate.
> - Aim for at least 3 points per year and at least 2 independent sources per constraint across <START>–<END>. Leave out anything dated outside that window.
> - Use these sources in priority order: primary datasets (Our World in Data, Santa Fe Performance Curve Database, BloombergNEF public summaries, IEA, NREL, USGS, BLS/FRED, academic learning-curve papers); then manufacturer and distributor price lists plus Wayback Machine snapshots; then reputable press and public report summaries.
> - For companies: give status (announced, deployed or paying) with an evidence URL. A funding announcement alone is "announced."
> After the CSV rows, add up to 5 lines describing coverage gaps.
