# Product & BizOps Analytics Case Study: Testing SAP's "Autonomous Enterprise" Narrative Against Its Own Q2 2026 Numbers

## Summary

SAP published its Q2 2026 results on July 23, 2026, built around a single strategic narrative: the "Autonomous Enterprise" — an AI-agent platform story reinforced by three acquisitions closed within a five-week window.

I treated this the way a Product/BizOps Analyst would treat any leadership narrative before it reaches a business review: as a claim to be tested, not a headline to be repeated. I built a relational data model directly from SAP's own published filings (Quarterly Statement, Results Presentation, Half-Year Report — all real, public, dated documents, not hypothetical data), defined four analytical questions the narrative implied, and wrote SQL — including window functions, a CTE, and a genuine cross-table JOIN — to answer them independently of SAP's own pre-computed summary figures.

This project also includes a Database Schema (DBML), Core Metrics, SQL Implementation, and a documented debugging pass to show how a real, same-day-published financial disclosure can be decomposed the way a Product Analyst would decompose any growth story — segment by segment, line item by line item, and checked against itself along the way.

## In this case study
- Project Context
- Business Problem
- Analytics Objective
- Data Model & Schema (DBML)
- Core Metrics
- SQL Implementation
- A Real Bug, Found and Fixed
- Findings & Business Impact
- Key Takeaways
- Disclaimer

## Project Context

SAP SE is one of the largest enterprise software vendors in the world. In its Q2 2026 Quarterly Statement, the company reported strong headline growth — current cloud backlog up 27% (26% at constant currency), cloud revenue up 22% (24% cc) — and framed this growth around a new strategic vision: the "Autonomous Enterprise," combining Joule (an AI agent layer), SAP Autonomous Suite, and SAP Business AI Platform. In the same reporting window, SAP closed or announced three acquisitions (Reltio, Dremio, Prior Labs) explicitly positioned as accelerants of this AI strategy.

For this case study, I focus on a specific analytics problem: **does the growth story support the AI narrative, or is the AI narrative currently riding on a separate, older growth driver (ERP cloud migration)?** This is a classic "narrative vs. mechanism" question — the kind a Product Analyst is asked to answer before a leadership story gets repeated uncritically in a board deck.

## Business Problem

Public companies routinely wrap real financial performance in a strategic narrative — this isn't unique to SAP, and it isn't necessarily misleading. But a narrative and its supporting mechanism can drift apart, and a company's own segment-level and product-line-level disclosures usually contain enough detail to check whether they still line up.

> The business challenge is:
>
> Is SAP's Q2 2026 growth actually attributable to its "Autonomous Enterprise" / AI strategy, or is it still primarily driven by legacy Cloud ERP Suite migration — with the AI narrative currently ahead of the mechanism that would sustain it?

<aside>
👉🏼 Why this matters
If growth is still migration-driven, near-term guidance is more exposed to ERP migration cadence than to AI product traction — a materially different risk profile than the one implied by the headline story, and the kind of gap a BizOps or Product Ops function would want surfaced before it's baked into planning assumptions.
</aside>

## Analyst Problem (the "user" of this analysis)

A Product Ops / BizOps analyst reading SAP's release faces the same problem an outside investor or a competing PM faces: the headline numbers (backlog +27%, cloud revenue +22%) are real, but they're aggregated, and some of them — including the growth percentages themselves — are pre-computed by SAP rather than independently derivable at a glance. Each of the following requires going one or two levels below the headline, and in some cases recomputing the numbers from raw line items rather than trusting the summary column:

- How much of that growth is the new AI-adjacent product surface vs. the decades-old ERP migration wave — computed from raw figures, not SAP's own growth-rate column?
- Is the company's own delivery organization (Core Services — the group that helps customers actually adopt new capability) scaling with the story, or shrinking?
- Does the "cost of the AI push" — the acquisition-related charges SAP flags as diluting profit — actually trace to the 2026 AI acquisitions, or is it inflated by older, unrelated M&A still amortizing?
- Do the customer wins SAP chose to publish actually skew AI, or mostly migration?

## Case Study Focus

This case study does not attempt a full equity-research valuation of SAP, and it does not offer investment advice. It focuses on **one specific analytical exercise**: building a queryable, joinable data model from SAP's own disclosed tables and using it — with real relational SQL, not just filtered lookups — to test whether the "Autonomous Enterprise" narrative is currently supported by the underlying line items, or running ahead of them.

## Analytics Objective

> 👉🏼 Product Analytics Question
> Does SAP's Q2 2026 growth trace to its AI-native product surface, or to legacy Cloud ERP Suite migration — and does the rest of the disclosure (segment profit, the real accounting footprint of its M&A, customer wins) corroborate or complicate the "Autonomous Enterprise" story?

The analysis answers four questions:
1. **Growth decomposition** — how much of cloud revenue growth is Cloud ERP Suite vs. Extension Suite vs. IaaS, computed independently rather than read off SAP's own growth-rate column?
2. **Segment tension** — is the services/enablement segment (Core Services) scaling with the product segment (ATS), or diverging from it?
3. **M&A's real accounting footprint** — does the disclosed profit drag of the one 2026 acquisition actually consolidated (Reltio) match the size of the "acquisition-related charges" addback for the whole quarter — a question that only a JOIN across two separate tables can answer?
4. **Customer win mix** — of the logos SAP chose to publish, how many are explicitly AI-tagged vs. migration-tagged?

## Data Model

Unlike a hypothetical case study, every table here is populated from SAP's actual published disclosures — the Quarterly Statement, the Results Presentation, and the Half-Year Report, all dated July 23, 2026. No values are simulated. Two tables — `acquisitions` and `opex_by_functional_area` — are used as a genuine relational pair, joined on reporting period to answer Q3; the rest are queried individually where a join wouldn't add anything (documented explicitly below, rather than forcing unnecessary joins for their own sake).

**Table 1: cloud_revenue_breakdown** — SaaS/PaaS, Cloud ERP Suite, Extension Suite, IaaS, by period and currency basis, with a real `period_end_date` so growth can be computed with a window function instead of string-sorted period labels
**Table 2: revenue_by_segment** — ATS vs. Core Services, by period and currency basis
**Table 3: acquisitions** — Reltio, Dremio, Prior Labs, with announce/close dates and P&L contribution
**Table 4: opex_by_functional_area** — IFRS-to-non-IFRS bridge by cost line, including the acquisition-related-charges addback that `acquisitions` joins against
**Table 5: customer_wins** — every named customer in the Business Highlights section, tagged by SAP's own category headings

*(Full 9-table schema, including revenue_by_region and headcount, lives in the accompanying repo.)*

### Database Architecture (DBML)

```
Table cloud_revenue_breakdown {
  id integer [primary key]
  period text
  period_type text
  period_end_date date // real date type — enables window-function ordering, not string luck
  line_item text // 'Cloud ERP Suite', 'Extension Suite', 'IaaS', 'SaaS/PaaS' (parent), 'Cloud revenue total'
  currency_basis text
  amount_eur_m float
  yoy_growth_pct float // SAP's own published figure — kept for reference, NOT used in analysis
}

Table revenue_by_segment {
  id integer [primary key]
  period text
  period_type text
  segment text // 'ATS' or 'Core Services'
  currency_basis text
  total_segment_revenue float
  segment_profit float
}

Table acquisitions {
  id integer [primary key]
  target_name text
  announced_date date
  closed_date date
  consideration_eur_m float
  q2_operating_profit_contribution_nonifrs_eur_m float
}

Table opex_by_functional_area {
  id integer [primary key]
  period text
  functional_area text
  ifrs_amount float
  acquisition_related_adj float // joined against acquisitions.q2_operating_profit_contribution_nonifrs_eur_m
  non_ifrs_amount float
}

Table customer_wins {
  id integer [primary key]
  customer_name text
  category text // 'RISE with SAP', 'SAP GROW', 'AI and data solutions', etc.
  period text
}
```

## Core Metrics

Before writing SQL, the same question as always: what actually proves or disproves the narrative — and can it be derived independently rather than borrowed from SAP's own summary columns?

**Primary Analytical Metric**
- **Cloud ERP Suite share of cloud revenue growth ($)** — computed via a window function (`LAG`) comparing each product line's current value to its prior-year value, not read from SAP's pre-computed growth-rate column
- Goal: if this is above ~90%, the AI narrative is running ahead of its supporting revenue mechanism

**Corroborating Metrics**
- Segment profit growth, ATS vs. Core Services (constant currency) — tests whether the enablement organization is scaling with the story
- Reltio's disclosed Q2 profit contribution vs. the total quarter's acquisition-related opex addback (via JOIN) — tests whether the "cost of AI" is really about 2026's acquisitions or is inflated by legacy M&A
- Named customer win count, by SAP's own category tag — tests whether publicized wins skew AI or migration

**Guardrail / Honesty Metric**
- % of findings that rely on SAP's own categorization or pre-computed figures (vs. independently derived from raw line items) — flagged explicitly per finding, so the analysis doesn't overstate its own objectivity

## SQL Implementation

With the schema defined, here are the actual queries run against the SQLite database built from SAP's tables.

### 1. Primary metric: Cloud ERP Suite share of growth — CTE + window function, independently derived

```sql
WITH growth AS (
    SELECT
        line_item,
        period_end_date,
        amount_eur_m,
        amount_eur_m - LAG(amount_eur_m) OVER (
            PARTITION BY line_item ORDER BY period_end_date
        ) AS delta_eur_m
    FROM cloud_revenue_breakdown
    WHERE period_type = 'quarter'
      AND line_item != 'SaaS/PaaS'   -- parent category of ERP Suite + Extension Suite; would double-count
      AND (
            (period = 'Q2 2026' AND currency_basis = 'constant')
         OR (period = 'Q2 2025' AND currency_basis = 'actual')
          )
)
SELECT
    line_item,
    delta_eur_m,
    ROUND(
        100.0 * delta_eur_m /
        (SELECT delta_eur_m FROM growth
         WHERE line_item = 'Cloud revenue total' AND delta_eur_m IS NOT NULL),
        1
    ) AS pct_of_total_cloud_growth
FROM growth
WHERE delta_eur_m IS NOT NULL
ORDER BY delta_eur_m DESC;
```
**Result:** Cloud ERP Suite +€1,103m = **95.8%** of total cloud revenue growth (+€1,151m); Extension Suite +€68m = 5.9%; IaaS -€20m = -1.7%. Independently derived from raw line items — and it matches SAP's own published growth rates, which is itself a useful cross-check that the underlying data was loaded correctly.

### 2. M&A's real footprint — a genuine cross-table JOIN

```sql
SELECT
    a.target_name,
    a.consideration_eur_m,
    a.q2_operating_profit_contribution_nonifrs_eur_m AS reltio_disclosed_q2_profit_drag,
    o.acquisition_related_adj AS total_quarter_acq_related_opex_addback
FROM acquisitions a
JOIN opex_by_functional_area o
    ON o.period = 'Q2 2026'
   AND o.functional_area = 'Total operating expenses'
WHERE a.target_name = 'Reltio';  -- only deal actually consolidated in Q2 2026 actuals
```
**Result:** Reltio's own disclosed Q2 drag = **-€8m** (non-IFRS operating profit). Total quarter acquisition-related opex addback = **€92m** — roughly **11.5x larger**. This is only visible by joining the acquisition-level table to the opex-level table; neither table alone shows the gap.

### 3. Segment profit divergence

```sql
SELECT period, segment, currency_basis, segment_profit, total_segment_revenue,
       ROUND(100.0 * segment_profit / total_segment_revenue, 1) AS margin_pct
FROM revenue_by_segment
WHERE period_type = 'half_year'
ORDER BY segment, currency_basis;
```
**Result:** ATS profit +15.2% (H1, constant currency); Core Services profit -17.3%.

### 4. Customer win categorization

```sql
SELECT category, COUNT(*) AS logo_count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customer_wins), 1) AS pct_of_total
FROM customer_wins
GROUP BY category
ORDER BY logo_count DESC;
```
**Result:** RISE with SAP 43.9%; AI and data solutions 19.5%; Went live 14.6%; SAP GROW 12.2%; Key portfolio win 9.8%.

## A Real Bug, Found and Fixed

The first version of Query 1 returned `NULL` for every percentage — not an error, just silent wrong output. The cause: the correlated subquery `(SELECT delta_eur_m FROM growth WHERE line_item = 'Cloud revenue total')` matched **two** rows in the CTE — the 2025 base-year row (where `LAG` has no prior value, so `delta_eur_m` is `NULL`) and the 2026 row (with the real delta). SQLite doesn't error on a scalar subquery that returns multiple rows; it just silently picks one — and it picked the `NULL` row, which propagated through every division.

The fix was a one-line filter (`AND delta_eur_m IS NOT NULL`) added to the subquery. The more useful fix was catching it at all: the query ran without error and produced output that *looked* plausible (correct row labels, correct deltas) with only the final column silently wrong — exactly the kind of bug that survives a quick eyeball check and only surfaces when someone deliberately verifies the output against hand math, the same discipline applied earlier in this project when the ATS/Core Services segment revenue was checked against reported total revenue before trusting it.

## Findings & Business Impact

- **Growth mechanism vs. narrative gap.** 95.8% of Q2's constant-currency cloud revenue growth — independently derived, not read from SAP's own growth column — came from Cloud ERP Suite, a well-understood on-premise-to-cloud migration wave, not new AI product adoption. The "Autonomous Enterprise" story is currently a layer on top of that migration tailwind, not yet an independent growth driver in the numbers.

- **Enablement is shrinking while product scales.** Core Services segment profit fell 17.3% (H1, constant currency) while the ATS product segment grew 15.2%. If AI-agent adoption genuinely depends on hands-on customer enablement — which SAP's own materials imply via its forward-deployed-engineering approach — a shrinking services arm is a plausible adoption bottleneck worth monitoring, not just a margin efficiency.

- **The "cost of AI" line is mostly legacy M&A.** The JOIN between `acquisitions` and `opex_by_functional_area` shows Reltio's own disclosed Q2 profit drag (-€8m) is roughly 11.5x smaller than the quarter's total acquisition-related opex addback (€92m). Most of that €92m almost certainly comes from amortization on SAP's older acquisitions, not the 2026 AI-strategy deals specifically — meaning the "cost of the AI push" reads larger in the aggregate P&L line than the AI acquisitions themselves actually show.

- **Published customer wins still skew migration.** Under 1 in 5 named customer logos in the release carry SAP's own "AI and data solutions" tag; the plurality (44%) are RISE with SAP migration stories.

**Estimated relevance for a Product Ops function:** if the growth-mechanism gap identified here holds through Q3, any internal planning that assumes AI-driven revenue acceleration (headcount allocation, roadmap prioritization tied to AI feature investment, partner-ecosystem bets) is currently being made ahead of the data that would justify it — a pattern worth flagging before it compounds across two or three more planning cycles.

## Key Takeaways & Project Learnings

> This case study tested a public company's strategic narrative against its own disclosed segment and product-line data, using the same "decompose before you believe the headline" discipline applied in the Zalando Fit Quiz case study — but against real, verifiable, same-day-published numbers, with real relational SQL doing real work, instead of a hypothetical dataset queried with flat lookups.

- **A narrative and its mechanism can be measured separately** — and the measurement should be derived, not borrowed. Trusting SAP's own growth-rate column would have made Finding 1 a summary, not an analysis; recomputing it with a window function made it independently verifiable.
- **Joins earn their place when they answer a question a single table can't.** The Reltio-vs-total-addback comparison doesn't exist in either the acquisitions table or the opex table alone — it only exists at the intersection, which is what a JOIN is actually for, as opposed to normalizing tables that are never queried together.
- **The most valuable bug is the one that doesn't crash.** A query that returns an error is easy to catch. A query that returns plausible-looking `NULL`s in exactly one column is the harder, more realistic failure mode — and the discipline that catches it (checking output against hand-calculated expectations) is the same discipline that caught the ATS/Core Services revenue reconciliation earlier in this project.
- **Real data raises the verification bar, and that's the point.** A hypothetical case study is judged on reasoning; a real one can be checked line-by-line against a public filing — including checking whether the SQL itself is doing genuine work or just decorating a small dataset.

---
---
---

> Disclaimer
This case study analyzes SAP SE's publicly published Q2 2026 Quarterly Statement, Results Presentation, and Half-Year Report (all released July 23, 2026, available at sap.com/investors). All figures cited are drawn directly from these public disclosures; the data model, SQL queries, findings, and business-impact framing are original analysis created for portfolio demonstration purposes. This is not investment research, not financial advice, and not an official SAP publication — it is an independent product/business analytics exercise.
