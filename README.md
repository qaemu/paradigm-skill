<div align="center">

<img alt="PARADIGMA: map how a field's constraints changed over the years you choose, and find what just became possible" src="assets/banner.svg" width="100%">

<br>

**An agent skill that maps how a field's constraints changed over the years you choose (20 by default),<br>to find where a new product, startup or line of research has just become possible.**

**English** | [Español](README/README_es.md) | [简体中文](README/README_cn.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-C9406B?style=flat-square&labelColor=111111)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-EE9AB3?style=flat-square&labelColor=111111)](skills/paradigma/scripts/paradigma.py)


[Quick start](#quick-start) · [Why](#why-constraints) · [How it works](#how-it-works) · [What you get](#what-you-get) · [Install](#install) · [Usage](#usage) · [Models](#which-model-to-run-it-on) · [The math](#the-math) · [Limits](#limits) · [FAQ](#faq)

</div>

---

## Quick start

```bash
npx skills add qaemu/paradigma-skill
```

Then, in your agent:

```text
/paradigma industrial maintenance
```

About an hour later you have a sourced report and a data workbook: which constraints in industrial maintenance fell, which are tightening, who is building on each, and where the gaps are.

> [!NOTE]
> PARADIGMA gives you a map, not a prediction. It shows where constraints moved and who has noticed. Deciding when to act, and on what, is still your job.

## Why constraints

Big shifts are rarely ideas nobody had before. Digital cash was attempted for twenty years before Bitcoin. Neural networks existed for decades before cheap GPUs and large datasets made them work. What usually changes is underneath: something gets 10× cheaper, a patent expires, a law takes effect, a skill stops being scarce, a norm shifts. An assumption the whole industry treats as fixed stops being true.

Those changes are usually public, so tracking them alone gives you no edge. The edge comes from comparing them against who is actually building on them. PARADIGMA does that comparison, for any field you name.

| It is | It is not |
|---|---|
| A sourced panorama of what changed in a field | An idea generator |
| Robust trends computed in code, with confidence grades | Numbers estimated in prose |
| A map of who is building on each change, and how far they got | A list of hyped startups |
| Explicit about gaps in its own data | A substitute for your judgment |

## How it works

<img alt="Eight steps: map the field, price curves, non-cost sweep, activity scan, gap matrix, why-not check, independent check, report" src="assets/pipeline.svg" width="100%">

| Step | What happens |
|---|---|
| **1. Map the field** | Breaks the field into 12–25 constraints: components, manufacturing, software and AI, data, labor, distribution, compliance, trust. Then a PESTEL sweep catches the political, economic, social, technological, environmental and legal ones. |
| **2. Price curves** | Helper agents collect historical data points in parallel, each with a link. The engine takes the median for each year, removes inflation and fits a robust trend that one bad value can't move. |
| **3. Non-cost sweep** | Official gazettes, standards bodies, patents expiring now, wage and shortage statistics, adoption surveys, export controls. Each change is dated and marked loosening or tightening. |
| **4. Activity scan** | Counts companies, funding, patents, papers and launches per constraint, with the same queries for every constraint. Each company is marked `announced`, `deployed` or `paying`, with evidence. |
| **5. Gap matrix** | Plots how far each constraint fell against how many are building on it. |
| **6. Why-not check** | Every gap is checked for failed attempts and remaining blockers before it's called an opportunity. |
| **7. Independent check** | A fresh agent that did none of the research re-opens the sources and checks every value. The report states the pass rate. |
| **8. Report** | A one-page panorama, one card per constraint, a timeline of dated changes, a company map, and a workbook with every data point and its link. |

### Rules it doesn't break

1. **No source, no number.** Data that can't be found is reported as missing, never estimated.
2. **All math runs in the engine** ([`paradigma.py`](skills/paradigma/scripts/paradigma.py)), not in the model's prose.
3. **A funding round is not traction.** Every company carries a status and the evidence behind it.
4. **Nothing is called white space until the why-not check has run.**
5. **Research is verified by an agent that didn't do it.**

## What you get

<div align="center">
<img alt="Gap matrix with four quadrants: white space, crowded, dormant, hype risk" src="assets/gap-matrix.svg" width="78%">
<br>
<sub>Illustration of the gap matrix. A real run plots your field's constraints.</sub>
</div>

<br>

| Quadrant | Meaning | What the report does with it |
|---|---|---|
| **White space** | The constraint fell far, and few are building on it | Runs the why-not check, then sorts each item into *untried*, *tried too early* (with the failed companies and dates) or *blocked* |
| **Crowded** | It fell far, and many are building | Lists the companies and how far each got. This is the consensus picture |
| **Hype risk** | Little changed, but many are building anyway | Flags it explicitly |
| **Dormant** | Little change and little activity | Kept for reference |

**Deliverables**

- **Report.** The panorama first: biggest drops, tightening constraints, white space, crowded zones, hype risks, and dated changes in the next 1–5 years such as laws taking effect and patents expiring. Then one card per constraint with its curve, yearly change and margin of error, fold change, trend shape, grade, thresholds, companies and why-not label. It ends with method, confidence and sources.
- **Workbook.** `constraints`, `points`, `periods`, `curves`, `noncost`, `companies`, `activity`, `gap_matrix`, `whynot` and `verification`. Every row has its source link.
- **Charts.** One log-scale curve per constraint, plus the gap matrix.

## Example

A full run on **predictive maintenance for industrial machinery** (2006–2025) is in [`examples/predictive-maintenance`](examples/predictive-maintenance). It has the report, the gap matrix, an Excel workbook with a *Start here* sheet that explains every term, and every data point with its source. The run is honest about what it couldn't find: the why-not check withdrew both white spaces the engine flagged on the first pass.

## Install

PARADIGMA follows the open [Agent Skills](https://agentskills.io) format: a `SKILL.md` plus a Python engine. Any agent that can browse the web, run Python and, ideally, start helper agents can use it.

### Any agent (skills CLI)

```bash
npx skills add qaemu/paradigma-skill                    # current project
npx skills add qaemu/paradigma-skill -g                 # all projects
npx skills add qaemu/paradigma-skill -a claude-code -a opencode
```

Uses the [skills CLI](https://github.com/vercel-labs/skills), which supports Claude Code, OpenCode, Codex, Cursor and many more.

### Claude Code

As a plugin, which gives you updates through `/plugin`:

```text
/plugin marketplace add qaemu/paradigma-skill
/plugin install paradigma@paradigma
```

Plugin skills are namespaced, so you run it as `/paradigma:paradigma <field>`.

Or as a personal skill, which you run as `/paradigma <field>`:

```bash
git clone https://github.com/qaemu/paradigma-skill.git
mkdir -p ~/.claude/skills && cp -r paradigma-skill/skills/paradigma ~/.claude/skills/
```

### Claude apps (web, desktop, mobile)

1. Download [`dist/paradigma.zip`](dist/paradigma.zip). It contains the `paradigma` folder with `SKILL.md` and the engine.
2. Turn on **Code execution and file creation** in **Settings → Capabilities**.
3. Go to **Customize → Skills**, click **+**, then **Create skill → Upload a skill**, and choose the ZIP.

See Anthropic's guide: [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

### OpenCode

```bash
git clone https://github.com/qaemu/paradigma-skill.git
mkdir -p ~/.config/opencode/skills && cp -r paradigma-skill/skills/paradigma ~/.config/opencode/skills/
```

OpenCode also reads `~/.claude/skills/`, so a Claude Code install works there too. Check that web search works with your provider first. Without it, PARADIGMA can't collect data.

### Requirements

| Needs | Why |
|---|---|
| Web search and page fetching | Every number comes from a source |
| Python 3.10+ with `pandas`, `numpy`, `matplotlib`, `openpyxl` (`scipy` optional) | The analysis engine, its charts and the Excel workbook |
| Helper agents (optional) | Parallel research and the independent check. Without them it runs one step at a time and marks the check as self-checked |
| `OPENALEX_API_KEY` (optional, [free](https://openalex.org)) | Paper counts once the shared free quota runs out. Without it those columns stay blank and the report says so |

## Usage

```text
/paradigma <field> [region] [years] [standard|deep]
```

| Argument | Default | Notes |
|---|---|---|
| `field` | required | If it's very broad, like *hardware* or *health*, PARADIGMA suggests 3–4 narrower subfields first. Narrower fields give much better results |
| `region` | global | Notes where the data is US- or EU-centric |
| `years` | `20` | How many years back to look, ending at the last full year. Write `10`, `10y` or `years=10` (5 to 50), or a range like `2010-2025`. Use 5–10 for fast fields, 20 for most hardware, 30+ for slow infrastructure. Short windows give fewer data points per curve, so grades are lower |
| depth | `standard` | `standard` covers 12–25 constraints. `deep` covers up to 40, with denser curves and why-not checks on every candidate |

```text
/paradigma agricultural machinery
/paradigma small-batch manufacturing Latin America
/paradigma lab instruments 2010-2025 deep
/paradigma dental aligners EU 10
```

> [!IMPORTANT]
> A standard run takes about an hour, with several agents working in parallel, and uses a substantial part of a plan's usage. `deep` takes longer. Pick the field before you start.

## Which model to run it on

What matters for this task is long-horizon reliability and discipline about sources. A fast model that fills a table with plausible numbers is the failure mode to avoid.

| Role | Recommended | Effort |
|---|---|---|
| Main run (planning, gap matrix, why-not, report) | Claude Opus 5.5 | high |
| Data-collection helpers | Claude Sonnet 5.5 | medium–high |
| Independent check | Opus 5.5, or Claude Fable 5.1 for `deep` runs | high |

Avoid small and "flash" models for the main run. To check any model, including free ones, run it on 3 constraints with well-published data, such as lithium-ion pack prices and solar module prices, then open every link it returns. **If it invents even one link or number, it fails.**

## The math

<details>
<summary><b>How the curves are computed</b></summary>

<br>

1. **Normalize.** Values are expressed per unit of performance ($/kWh, $ per sensor channel, $/kg payload). USD values are converted to constant dollars with US CPI from FRED. Non-USD values need a cited exchange rate, or they're rejected.
2. **Bin.** Data is grouped by year, or by quarter when it's dense enough: at least 3 points in at least 60% of quarters, and at least 8 quarters. Each period keeps its median, its interquartile range and its count, and periods with fewer than 3 points are flagged.
3. **Fit.** A Theil–Sen line is fitted on log₁₀ of the period medians, so each period gets one vote and outliers barely move it. The slope gives the yearly % change with a 95% confidence interval. The engine never reports an endpoint-to-endpoint percentage as a trend.
4. **Shape.** The last 5 years are compared with the whole window to classify the trend as accelerating, steady or decelerating.
5. **Classify.** Each curve is *improved ≥10×*, *improving*, *flat / unclear*, or *worsening (constraint tightening)*. The direction depends on whether lower or higher is better for that metric.
6. **Grade.**

| Grade | Requires |
|---|---|
| A | ≥ 8 periods, ≥ 3 independent sources, ≤ 20% thin periods, tight confidence interval |
| B | ≥ 5 periods, ≥ 2 sources |
| C | usable but weak. Can't support a headline claim |
| D | fewer than 3 periods. No trend computed |

</details>

<details>
<summary><b>How the gap matrix is scored</b></summary>

<br>

- **Drop score.** The percentile rank of each constraint's improvement per decade (log₁₀ of the fold change). Non-cost constraints are scored 0–3 from the evidence, with a written justification. Crossing a viability threshold adds a bonus.
- **Activity score.** The mean percentile rank of the log-scaled companies, funding, patents, launches and job postings that are available. Missing signals are skipped, not counted as zero.
- **Research ahead of companies.** Papers in the last 3 years divided by (companies + 1). When research is far ahead of companies, the gap score goes up.
- **Gap score** = drop score × (1 − activity score), weighted by research-ahead. Quadrants split at the median.

These scores are relative. They rank the constraints of one field against each other, not against an absolute scale.

</details>

<details>
<summary><b>Run the engine on its own</b></summary>

<br>

```bash
cd skills/paradigma/scripts
python3 paradigma.py cpi                  # US CPI annual averages from FRED
python3 paradigma.py curves --start 2006 --end 2025 --plots   # points.csv -> curves.csv, periods.csv, plots/
python3 paradigma.py papers --start 2005 --end 2025   # OpenAlex paper counts
python3 paradigma.py gap --plots          # curves + activity -> gap_matrix.csv, plots/gap_matrix.png
python3 paradigma.py workbook --field "…" --start 2006 --end 2025   # every table -> readable .xlsx
```

The CSV schemas are in [`SKILL.md`, Appendix B](skills/paradigma/SKILL.md#appendix-b-csv-schemas).

</details>

## Data sources

Every source PARADIGMA uses is free. The report says where paid databases would add more.

| Need | Used by PARADIGMA (free) | What professionals add (paid) |
|---|---|---|
| Cost curves | Our World in Data, Santa Fe Performance Curve Database, BLS / FRED, USGS, NREL, IEA, price lists + Wayback Machine | BloombergNEF, teardown firms |
| Companies and funding | Press releases, free Crunchbase / Dealroom pages, startup directories | PitchBook, CB Insights, Crunchbase Pro |
| Patents | Google Patents, Lens.org | PatSnap, Derwent |
| Research papers | OpenAlex | Scopus, Web of Science |
| Regulation | Official gazettes (Federal Register, EUR-Lex, national gazettes), ISO / IEC / SAE | Legal trackers |

## Limits

- **Funding data is the weakest signal.** Free sources miss undisclosed rounds and many non-US companies.
- **Statistics lean US and EU.** The report flags regional bias.
- **Being too early looks the same as being wrong.** Drops less than 3 years old are flagged as *early*.
- **Activity driven by speculation is not adoption.** The report separates hype from users with a need.
- **Status: v0.1, experimental.** The engine passes an offline test suite on synthetic data with known answers. One full real run is published in [`examples/predictive-maintenance`](examples/predictive-maintenance); it also exposed and fixed an engine bug.

## FAQ

**Does it touch my files or accounts?**
No. It reads public websites and writes only to its own working folder. It doesn't sign in anywhere.

**Why not ask a model for a market report directly?**
Because it will give you one, numbers included, and you won't be able to tell which numbers it invented. PARADIGMA requires a source for every number, does the math in code, and has a separate agent check the work.

**Can I use it on a free model?**
Yes, if the model passes the test in [Which model to run it on](#which-model-to-run-it-on). Check each provider's data policy first, since some free models train on your prompts.

**How is this different from a consultant's market report?**
A market report sizes a market. PARADIGMA asks which assumptions behind a market stopped being true, and who has noticed.

## Repository

```text
paradigma-skill/
├── .claude-plugin/          Claude Code marketplace + plugin manifests
├── skills/paradigma/
│   ├── SKILL.md             instructions the agent follows
│   └── scripts/paradigma.py analysis engine (curves, gap matrix, CPI, papers)
├── tests/test_engine.py     offline test with known answers
├── examples/               a full real run (predictive maintenance)
├── dist/paradigma.zip       ready-to-upload skill for Claude apps (tools/package.sh)
├── tools/                   make_assets.py (README artwork), package.sh (rebuilds the ZIP)
├── README/                  translations of this page
└── assets/                  banner, pipeline and gap-matrix art
```

```bash
python3 tests/test_engine.py   # expect 15 PASS lines
```

## Contributing

Issues and pull requests are welcome, especially:

- real runs you're willing to share in `examples/`
- better free data sources for a specific field or region
- cases where a gap PARADIGMA reported turned out to be wrong, and why

Keep the rules intact: every number gets a source, and all math stays in the engine.

## License

[MIT](LICENSE) © 2026 qaemu

<div align="center">
<br>
<sub>Built by <a href="https://github.com/qaemu">qaemu</a>. Also by the same author: <a href="https://github.com/qaemu/phasentic">Phasentic</a>, open-source powder XRD phase identification.</sub>
</div>
