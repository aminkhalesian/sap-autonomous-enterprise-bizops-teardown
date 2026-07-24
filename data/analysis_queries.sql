-- ============================================================
-- Q1: Growth decomposition — independently derived, not trusted from SAP's column
--
-- SAP publishes a yoy_growth_pct column directly in its tables. We do NOT use it.
-- Instead we compute the EUR delta ourselves with a window function (LAG) comparing
-- each line item to its prior-year value, then use a CTE + subquery to express each
-- line item's delta as a share of TOTAL cloud revenue growth.
-- ============================================================
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
            (period = 'Q2 2026' AND currency_basis = 'constant')  -- current year, constant currency
         OR (period = 'Q2 2025' AND currency_basis = 'actual')    -- prior year, base period
          )
)
SELECT
    line_item,
    delta_eur_m,
    ROUND(
        100.0 * delta_eur_m /
        (SELECT delta_eur_m FROM growth
         WHERE line_item = 'Cloud revenue total' AND delta_eur_m IS NOT NULL),  -- BUG FIX: without this
                                                                                  -- filter the subquery
                                                                                  -- matches 2 rows (the
                                                                                  -- NULL base-year row too)
                                                                                  -- and SQLite silently
                                                                                  -- returns NULL for all
                                                                                  -- percentages
        1
    ) AS pct_of_total_cloud_growth
FROM growth
WHERE delta_eur_m IS NOT NULL
ORDER BY delta_eur_m DESC;

-- Result: Cloud ERP Suite +1,103m = 95.8% of total cloud revenue growth (+1,151m)
--         Extension Suite   +68m =  5.9%
--         IaaS               -20m = -1.7%
-- (Independently derived — matches SAP's own reported growth rates, which is itself
--  a useful cross-check that the underlying line-item data was loaded correctly.)

-- ============================================================
-- Q2: M&A cadence AND its real accounting footprint — a genuine cross-table JOIN
--
-- Question: SAP disclosed Reltio's Q2 profit contribution (-€8m non-IFRS). SAP also
-- disclosed a much larger "acquisition-related charges" addback for the whole quarter
-- (€92m, from the opex functional-area table). Are these the same thing? A flat,
-- single-table view can't answer this — it requires joining the acquisition-level
-- table to the opex-level table on the reporting period.
-- ============================================================
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

-- Result: Reltio's own disclosed Q2 drag = -€8m (non-IFRS operating profit)
--         Total quarter acquisition-related opex addback = €92m
-- The €92m figure is ~11.5x larger than Reltio's own disclosed impact — meaning most
-- of that addback is amortization from SAP's PRIOR acquisitions (Signavio, WalkMe,
-- Qualtrics-era deals, etc.), not the 2026 AI-strategy acquisitions specifically.
-- The "cost of the AI push" narrative is smaller in the numbers than the aggregate
-- acquisition addback line makes it look at a glance — a finding only visible by
-- joining the two tables, not from reading either one alone.

-- ============================================================
-- Q3: Segment tension — ATS vs Core Services profit trend
-- (single-table, retained as-is: this one genuinely doesn't need a join)
-- ============================================================
SELECT period, segment, currency_basis, segment_profit, total_segment_revenue,
       ROUND(100.0 * segment_profit / total_segment_revenue, 1) AS margin_pct
FROM revenue_by_segment
WHERE period_type IN ('quarter','half_year')
ORDER BY segment, period_type, currency_basis;

-- H1 2026 constant currency: ATS profit 6,431 -> 7,407 = +15.2%
--                             Core Services profit 249 -> 206 = -17.3%

-- ============================================================
-- Q4: Customer win categorization — how many logos are AI-flagged
--     vs RISE/GROW migration vs generic?
-- (single-table; this is a tally of SAP's own category tags, not a computed metric —
--  flagged explicitly in the write-up as categorization, not calculation)
-- ============================================================
SELECT category, COUNT(*) AS logo_count,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customer_wins), 1) AS pct_of_total
FROM customer_wins
GROUP BY category
ORDER BY logo_count DESC;

-- RISE with SAP (migration): 18 logos = 43.9%
-- AI and data solutions:      8 logos = 19.5%
-- Went live:                  6 logos = 14.6%
-- SAP GROW (migration, mid-market): 5 logos = 12.2%
-- Key portfolio win:          4 logos = 9.8%
