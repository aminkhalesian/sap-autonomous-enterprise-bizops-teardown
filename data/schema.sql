-- SAP Q2 2026 Teardown — Schema
-- Source: SAP Quarterly Statement Q2 2026, Results Presentation, Half-Year Report 2026
-- Built: July 23, 2026 (same-day as report release)

PRAGMA foreign_keys = ON;

-- ============================================================
-- Revenue by segment (ATS vs Core Services) — non-IFRS, quarterly + H1
-- ============================================================
CREATE TABLE revenue_by_segment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,              -- 'Q2 2026', 'Q2 2025', 'Q1-Q2 2026', 'Q1-Q2 2025'
    period_type TEXT NOT NULL CHECK (period_type IN ('quarter','half_year')),
    segment TEXT NOT NULL CHECK (segment IN ('ATS','Core Services')),
    currency_basis TEXT NOT NULL CHECK (currency_basis IN ('actual','constant')),
    cloud_revenue REAL,
    software_licenses_revenue REAL,
    software_support_revenue REAL,
    cloud_and_software_revenue REAL,
    services_revenue REAL,
    total_segment_revenue REAL,
    cost_of_revenue REAL,
    segment_gross_profit REAL,
    other_segment_expenses REAL,
    segment_profit REAL
);

-- ============================================================
-- Revenue by region (EMEA / Americas / APJ, + country detail)
-- ============================================================
CREATE TABLE revenue_by_region (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('quarter','half_year')),
    region TEXT NOT NULL,              -- 'Germany','Rest of EMEA','EMEA','United States','Rest of Americas',
                                        -- 'Americas','Japan','Rest of APJ','APJ'
    currency_basis TEXT NOT NULL CHECK (currency_basis IN ('actual','constant')),
    cloud_revenue REAL,
    cloud_and_software_revenue REAL,
    total_revenue REAL
);

-- ============================================================
-- Cloud revenue growth decomposition (SaaS/PaaS split incl. Cloud ERP Suite, Extension Suite, IaaS)
-- ============================================================
CREATE TABLE cloud_revenue_breakdown (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('quarter','half_year')),
    period_end_date DATE NOT NULL,     -- real date, so window functions order correctly (not string luck)
    line_item TEXT NOT NULL,           -- 'SaaS/PaaS','Cloud ERP Suite','Extension Suite','IaaS','Cloud revenue total'
    currency_basis TEXT NOT NULL CHECK (currency_basis IN ('actual','constant')),
    amount_eur_m REAL,
    yoy_growth_pct REAL                -- SAP's own published figure — kept for reference only, NOT used in analysis
);

-- ============================================================
-- Operating expenses by functional area (IFRS vs non-IFRS)
-- ============================================================
CREATE TABLE opex_by_functional_area (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('quarter','half_year')),
    functional_area TEXT NOT NULL,     -- 'Cost of cloud','R&D','Sales and marketing','G&A','Restructuring', etc.
    ifrs_amount REAL,
    acquisition_related_adj REAL,
    restructuring_adj REAL,
    teradata_litigation_adj REAL,
    non_ifrs_amount REAL
);

-- ============================================================
-- Non-IFRS adjustments (actuals + full-year estimates)
-- ============================================================
CREATE TABLE non_ifrs_adjustments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,
    adjustment_type TEXT NOT NULL,     -- 'Acquisition-related charges','Restructuring','Teradata litigation','Equity securities gains/losses'
    amount_eur_m REAL,
    is_estimate INTEGER DEFAULT 0,     -- 1 if FY2026 estimate, 0 if actual
    estimate_range_low REAL,
    estimate_range_high REAL
);

-- ============================================================
-- Acquisitions (M&A cadence — the "narrative vs discipline" question)
-- ============================================================
CREATE TABLE acquisitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_name TEXT NOT NULL,
    announced_date TEXT,
    closed_date TEXT,
    consideration_eur_m REAL,
    consideration_type TEXT,           -- 'cash','cash+share-based','cash+other'
    strategic_category TEXT,           -- 'MDM/master data','data lakehouse','tabular foundation models'
    segment_assigned TEXT,             -- 'ATS' etc.
    q2_revenue_contribution_eur_m REAL,
    q2_operating_profit_contribution_ifrs_eur_m REAL,
    q2_operating_profit_contribution_nonifrs_eur_m REAL,
    notes TEXT
);

-- ============================================================
-- Customer wins (Business Highlights section) — tagged by category
-- ============================================================
CREATE TABLE customer_wins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('RISE with SAP','SAP GROW','AI and data solutions','Key portfolio win','Went live')),
    period TEXT NOT NULL DEFAULT 'Q2 2026'
);

-- ============================================================
-- Headcount by function and region
-- ============================================================
CREATE TABLE headcount (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,              -- '6/30/2026','6/30/2025'
    function_area TEXT NOT NULL,       -- 'Cloud and software','Services','R&D','Sales and marketing','G&A','Infrastructure'
    region TEXT NOT NULL,              -- 'EMEA','Americas','APJ','Total'
    fte_count REAL
);

-- ============================================================
-- Key financial KPIs (top-line, for quick dashboard reference)
-- ============================================================
CREATE TABLE key_kpis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('quarter','half_year')),
    metric_name TEXT NOT NULL,
    ifrs_value REAL,
    non_ifrs_value REAL,
    unit TEXT                          -- 'EUR_m','pct','EUR_per_share'
);
