# SAP Autonomous Enterprise — A BizOps Teardown of Q2 2026 Results

Testing SAP's "Autonomous Enterprise" AI narrative against its own published Q2 2026 segment and product-line data — built same-day from the public filing (July 23, 2026).

**📄 Full case study:** [Read on Notion →](#) <!-- replace with Notion link -->
**📊 Dashboard:** [Open interactive dashboard →](./sap_q2_2026_teardown_dashboard.html)

## Headline finding

95.8% of Q2's cloud revenue growth traced to legacy Cloud ERP Suite migration, not the new AI product surface — while Core Services (customer enablement) profit fell 17.3% as the core product segment grew 15.2%. The AI narrative is currently ahead of the mechanism that would sustain it.

## Repo structure

```
├── schema.sql              # SQLite schema — 9 tables
├── etl_load.py              # ETL script, source filings → SQLite
├── analysis_queries.sql     # The 4 analytical queries behind the findings
├── sap_q2_2026.db           # Populated SQLite database
└── dashboard.html           # Standalone interactive dashboard (Chart.js)
```

## Stack

`SQLite` · `Python` · `SQL` · `HTML/CSS/JS` + `Chart.js` — architecture and logic directed by me, implementation generated and debugged with Claude against real source data.

## Source

SAP SE, Quarterly Statement Q2 2026, Results Presentation, and Half-Year Report 2026 (published July 23, 2026, sap.com/investors).

*Independent portfolio analysis — not an official SAP publication, investment research, or financial advice.*

---
**Amin Khalesian** — [LinkedIn](https://linkedin.com/in/aminkhalesian) · [GitHub](https://github.com/aminkhalesian)
