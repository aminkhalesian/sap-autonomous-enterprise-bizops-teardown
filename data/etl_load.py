"""
ETL loader for SAP Q2 2026 Teardown database.
Source: SAP Quarterly Statement Q2 2026, Q2 2026 Results Presentation,
        SAP Half-Year Report 2026 (all released July 23, 2026).

Run: python3 etl_load.py
"""
import sqlite3

DB_PATH = "sap_q2_2026.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def build_schema(conn):
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()

# ---------------------------------------------------------------
# 1. revenue_by_segment
# ---------------------------------------------------------------
def load_revenue_by_segment(conn):
    rows = [
        # period, period_type, segment, currency_basis,
        # cloud_rev, sw_lic_rev, sw_supp_rev, cloud_sw_rev, services_rev,
        # total_seg_rev, cost_of_rev, seg_gross_profit, other_seg_exp, seg_profit
        ("Q2 2026", "quarter", "ATS", "actual",
         6281, 131, 2439, 8851, 61, 8912, -1851, 7061, -3504, 3557),
        ("Q2 2026", "quarter", "ATS", "constant",
         6381, 131, 2467, 8980, 61, 9041, -1878, 7163, -3534, 3629),
        ("Q2 2025", "quarter", "ATS", "actual",
         5130, 194, 2642, 7966, 69, 8034, -1593, 6441, -3150, 3291),

        ("Q2 2026", "quarter", "Core Services", "actual",
         None, None, None, None, 966, 966, -720, 245, -153, 92),
        ("Q2 2026", "quarter", "Core Services", "constant",
         None, None, None, None, 977, 977, -726, 251, -154, 97),
        ("Q2 2025", "quarter", "Core Services", "actual",
         None, None, None, None, 992, 992, -718, 274, -136, 139),

        ("Q1-Q2 2026", "half_year", "ATS", "actual",
         12244, 247, 4908, 17399, 123, 17522, -3616, 13906, -6768, 7137),
        ("Q1-Q2 2026", "half_year", "ATS", "constant",
         12708, 254, 5053, 18014, 126, 18140, -3771, 14369, -6963, 7407),
        ("Q1-Q2 2025", "half_year", "ATS", "actual",
         10124, 377, 5403, 15904, 147, 16051, -3192, 12859, -6428, 6431),

        ("Q1-Q2 2026", "half_year", "Core Services", "actual",
         None, None, None, None, 1910, 1910, -1427, 483, -296, 187),
        ("Q1-Q2 2026", "half_year", "Core Services", "constant",
         None, None, None, None, 1974, 1974, -1465, 509, -303, 206),
        ("Q1-Q2 2025", "half_year", "Core Services", "actual",
         None, None, None, None, 1989, 1989, -1455, 534, -285, 249),
    ]
    conn.executemany("""
        INSERT INTO revenue_by_segment
        (period, period_type, segment, currency_basis, cloud_revenue,
         software_licenses_revenue, software_support_revenue, cloud_and_software_revenue,
         services_revenue, total_segment_revenue, cost_of_revenue, segment_gross_profit,
         other_segment_expenses, segment_profit)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
# 2. revenue_by_region
# ---------------------------------------------------------------
def load_revenue_by_region(conn):
    rows = []
    # Q2 2026 actual/constant, total revenue by region
    q2_2026_total = [
        ("Germany", "actual", 1560), ("Germany", "constant", 1561),
        ("Rest of EMEA", "actual", 3043), ("Rest of EMEA", "constant", 3041),
        ("EMEA", "actual", 4603), ("EMEA", "constant", 4602),
        ("United States", "actual", 3037), ("United States", "constant", 3113),
        ("Rest of Americas", "actual", 844), ("Rest of Americas", "constant", 837),
        ("Americas", "actual", 3881), ("Americas", "constant", 3950),
        ("Japan", "actual", 384), ("Japan", "constant", 431),
        ("Rest of APJ", "actual", 1009), ("Rest of APJ", "constant", 1035),
        ("APJ", "actual", 1394), ("APJ", "constant", 1466),
    ]
    for region, basis, total_rev in q2_2026_total:
        rows.append(("Q2 2026", "quarter", region, basis, None, None, total_rev))

    q2_2025_total = [
        ("Germany", 1412), ("Rest of EMEA", 2746), ("EMEA", 4158),
        ("United States", 2829), ("Rest of Americas", 725), ("Americas", 3554),
        ("Japan", 392), ("Rest of APJ", 923), ("APJ", 1315),
    ]
    for region, total_rev in q2_2025_total:
        rows.append(("Q2 2025", "quarter", region, "actual", None, None, total_rev))

    # Q2 2026 cloud revenue + cloud&software revenue by macro-region (EMEA/Americas/APJ)
    q2_2026_cloud = [
        ("EMEA", "actual", 2737, 4128), ("EMEA", "constant", 2741, 4128),
        ("Americas", "actual", 2631, 3453), ("Americas", "constant", 2677, 3513),
        ("APJ", "actual", 913, 1270), ("APJ", "constant", 964, 1338),
    ]
    for region, basis, cloud_rev, cs_rev in q2_2026_cloud:
        rows.append(("Q2 2026", "quarter", region, basis, cloud_rev, cs_rev, None))

    q2_2025_cloud = [
        ("EMEA", 2163, 3669), ("Americas", 2215, 3106), ("APJ", 753, 1191),
    ]
    for region, cloud_rev, cs_rev in q2_2025_cloud:
        rows.append(("Q2 2025", "quarter", region, "actual", cloud_rev, cs_rev, None))

    # H1 2026 / H1 2025 total revenue by region
    h1_2026_total = [
        ("Germany", "actual", 3086), ("Germany", "constant", 3089),
        ("Rest of EMEA", "actual", 5996), ("Rest of EMEA", "constant", 6042),
        ("EMEA", "actual", 9082), ("EMEA", "constant", 9131),
        ("United States", "actual", 5968), ("United States", "constant", 6356),
        ("Rest of Americas", "actual", 1629), ("Rest of Americas", "constant", 1668),
        ("Americas", "actual", 7597), ("Americas", "constant", 8024),
        ("Japan", "actual", 773), ("Japan", "constant", 873),
        ("Rest of APJ", "actual", 1980), ("Rest of APJ", "constant", 2085),
        ("APJ", "actual", 2753), ("APJ", "constant", 2959),
    ]
    for region, basis, total_rev in h1_2026_total:
        rows.append(("Q1-Q2 2026", "half_year", region, basis, None, None, total_rev))

    h1_2025_total = [
        ("Germany", 2791), ("Rest of EMEA", 5400), ("EMEA", 8191),
        ("United States", 5781), ("Rest of Americas", 1437), ("Americas", 7219),
        ("Japan", 789), ("Rest of APJ", 1841), ("APJ", 2630),
    ]
    for region, total_rev in h1_2025_total:
        rows.append(("Q1-Q2 2025", "half_year", region, "actual", None, None, total_rev))

    # H1 2026 cloud + cloud&software by macro-region
    h1_2026_cloud = [
        ("EMEA", "actual", 5321, 8119), ("EMEA", "constant", 5366, 8165),
        ("Americas", "actual", 5147, 6765), ("Americas", "constant", 5431, 7143),
        ("APJ", "actual", 1775, 2515), ("APJ", "constant", 1911, 2706),
    ]
    for region, basis, cloud_rev, cs_rev in h1_2026_cloud:
        rows.append(("Q1-Q2 2026", "half_year", region, basis, cloud_rev, cs_rev, None))

    h1_2025_cloud = [
        ("EMEA", 4195, 7208), ("Americas", 4446, 6315), ("APJ", 1483, 2382),
    ]
    for region, cloud_rev, cs_rev in h1_2025_cloud:
        rows.append(("Q1-Q2 2025", "half_year", region, "actual", cloud_rev, cs_rev, None))

    conn.executemany("""
        INSERT INTO revenue_by_region
        (period, period_type, region, currency_basis, cloud_revenue, cloud_and_software_revenue, total_revenue)
        VALUES (?,?,?,?,?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
# 3. cloud_revenue_breakdown (growth decomposition — core to sub-question 1)
# ---------------------------------------------------------------
def load_cloud_revenue_breakdown(conn):
    rows = [
        # period, period_type, period_end_date, line_item, currency_basis, amount_eur_m, yoy_growth_pct(SAP's, ref only)
        # --- Q2 2026 (current quarter) ---
        ("Q2 2026", "quarter", "2026-06-30", "SaaS/PaaS", "actual", 6216, 23),
        ("Q2 2026", "quarter", "2026-06-30", "SaaS/PaaS", "constant", 6216, 25),
        ("Q2 2026", "quarter", "2026-06-30", "Cloud ERP Suite", "actual", 5525, 25),
        ("Q2 2026", "quarter", "2026-06-30", "Cloud ERP Suite", "constant", 5525, 27),
        ("Q2 2026", "quarter", "2026-06-30", "Extension Suite", "actual", 692, 11),
        ("Q2 2026", "quarter", "2026-06-30", "Extension Suite", "constant", 692, 12),
        ("Q2 2026", "quarter", "2026-06-30", "IaaS", "actual", 65, -23),
        ("Q2 2026", "quarter", "2026-06-30", "IaaS", "constant", 65, -22),
        ("Q2 2026", "quarter", "2026-06-30", "Cloud revenue total", "actual", 6281, 22),
        ("Q2 2026", "quarter", "2026-06-30", "Cloud revenue total", "constant", 6281, 24),

        # --- Q2 2025 (prior-year quarter, actual currency only — this is the base period) ---
        ("Q2 2025", "quarter", "2025-06-30", "SaaS/PaaS", "actual", 5045, None),
        ("Q2 2025", "quarter", "2025-06-30", "Cloud ERP Suite", "actual", 4422, None),
        ("Q2 2025", "quarter", "2025-06-30", "Extension Suite", "actual", 624, None),
        ("Q2 2025", "quarter", "2025-06-30", "IaaS", "actual", 85, None),
        ("Q2 2025", "quarter", "2025-06-30", "Cloud revenue total", "actual", 5130, None),

        # --- Q1-Q2 2026 (current half-year) ---
        ("Q1-Q2 2026", "half_year", "2026-06-30", "SaaS/PaaS", "actual", 12112, 22),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "SaaS/PaaS", "constant", 12112, 27),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "Cloud ERP Suite", "actual", 10739, 24),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "Cloud ERP Suite", "constant", 10739, 29),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "Extension Suite", "actual", 1373, 9),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "Extension Suite", "constant", 1373, 12),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "IaaS", "actual", 131, -30),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "IaaS", "constant", 131, -28),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "Cloud revenue total", "actual", 12244, 21),
        ("Q1-Q2 2026", "half_year", "2026-06-30", "Cloud revenue total", "constant", 12244, 26),

        # --- Q1-Q2 2025 (prior-year half-year, actual currency only — base period) ---
        ("Q1-Q2 2025", "half_year", "2025-06-30", "SaaS/PaaS", "actual", 9935, None),
        ("Q1-Q2 2025", "half_year", "2025-06-30", "Cloud ERP Suite", "actual", 8673, None),
        ("Q1-Q2 2025", "half_year", "2025-06-30", "Extension Suite", "actual", 1262, None),
        ("Q1-Q2 2025", "half_year", "2025-06-30", "IaaS", "actual", 188, None),
        ("Q1-Q2 2025", "half_year", "2025-06-30", "Cloud revenue total", "actual", 10124, None),
    ]
    conn.executemany("""
        INSERT INTO cloud_revenue_breakdown
        (period, period_type, period_end_date, line_item, currency_basis, amount_eur_m, yoy_growth_pct)
        VALUES (?,?,?,?,?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
# 4. opex_by_functional_area (IFRS -> non-IFRS bridge)
# ---------------------------------------------------------------
def load_opex(conn):
    rows = [
        # period, period_type, functional_area, ifrs, acq_adj, restr_adj, teradata_adj, non_ifrs
        ("Q2 2026", "quarter", "Cost of cloud", -1617, 23, 0, 0, -1595),
        ("Q2 2026", "quarter", "Cost of software licenses and support", -263, 0, 0, 0, -263),
        ("Q2 2026", "quarter", "Cost of services", -769, 0, 0, 0, -769),
        ("Q2 2026", "quarter", "Research and development", -1844, 1, 0, 0, -1843),
        ("Q2 2026", "quarter", "Sales and marketing", -2315, 57, 0, 0, -2258),
        ("Q2 2026", "quarter", "General and administration", -404, 12, 0, 0, -392),
        ("Q2 2026", "quarter", "Restructuring", -7, 0, 7, 0, 0),
        ("Q2 2026", "quarter", "Other operating income/expense, net", -14, 0, 0, 0, -14),
        ("Q2 2026", "quarter", "Total operating expenses", -7235, 92, 7, 0, -7135),

        ("Q2 2025", "quarter", "Cost of cloud", -1297, 23, 0, 0, -1274),
        ("Q2 2025", "quarter", "Cost of software licenses and support", -313, 0, 0, 0, -313),
        ("Q2 2025", "quarter", "Cost of services", -797, 0, 0, 0, -797),
        ("Q2 2025", "quarter", "Research and development", -1618, 1, 0, 0, -1616),
        ("Q2 2025", "quarter", "Sales and marketing", -2156, 68, 0, 0, -2088),
        ("Q2 2025", "quarter", "General and administration", -361, 1, 0, 0, -360),
        ("Q2 2025", "quarter", "Restructuring", -18, 0, 18, 0, 0),
        ("Q2 2025", "quarter", "Other operating income/expense, net", -11, 0, 0, 0, -11),
        ("Q2 2025", "quarter", "Total operating expenses", -6571, 94, 18, 0, -6459),

        ("Q1-Q2 2026", "half_year", "Cost of cloud", -3130, 45, 0, 9, -3076),
        ("Q1-Q2 2026", "half_year", "Cost of software licenses and support", -559, 0, 0, 9, -550),
        ("Q1-Q2 2026", "half_year", "Cost of services", -1543, 0, 0, 0, -1544),
        ("Q1-Q2 2026", "half_year", "Research and development", -3546, 2, 0, 0, -3543),
        ("Q1-Q2 2026", "half_year", "Sales and marketing", -4455, 114, 0, 0, -4341),
        ("Q1-Q2 2026", "half_year", "General and administration", -762, 17, 0, 12, -734),
        ("Q1-Q2 2026", "half_year", "Restructuring", -19, 0, 19, 0, 0),
        ("Q1-Q2 2026", "half_year", "Other operating income/expense, net", -36, 0, 0, 0, -36),
        ("Q1-Q2 2026", "half_year", "Total operating expenses", -14049, 177, 19, 29, -13823),

        ("Q1-Q2 2025", "half_year", "Cost of cloud", -2570, 48, 0, 0, -2523),
        ("Q1-Q2 2025", "half_year", "Cost of software licenses and support", -605, 0, 0, 0, -605),
        ("Q1-Q2 2025", "half_year", "Cost of services", -1638, 1, 0, 0, -1637),
        ("Q1-Q2 2025", "half_year", "Research and development", -3291, 3, 0, 0, -3288),
        ("Q1-Q2 2025", "half_year", "Sales and marketing", -4391, 163, 0, 0, -4228),
        ("Q1-Q2 2025", "half_year", "General and administration", -719, 2, 0, 0, -717),
        ("Q1-Q2 2025", "half_year", "Restructuring", -18, 0, 18, 0, 0),
        ("Q1-Q2 2025", "half_year", "Other operating income/expense, net", -19, 0, 0, 0, -19),
        ("Q1-Q2 2025", "half_year", "Total operating expenses", -13251, 217, 18, 0, -13016),
    ]
    conn.executemany("""
        INSERT INTO opex_by_functional_area
        (period, period_type, functional_area, ifrs_amount, acquisition_related_adj,
         restructuring_adj, teradata_litigation_adj, non_ifrs_amount)
        VALUES (?,?,?,?,?,?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
# 5. non_ifrs_adjustments (actuals + FY2026 estimate ranges)
# ---------------------------------------------------------------
def load_non_ifrs_adjustments(conn):
    rows = [
        # period, adjustment_type, amount, is_estimate, range_low, range_high
        ("FY2026E", "Acquisition-related charges", None, 1, 340, 420),
        ("FY2026E", "Restructuring", None, 1, 0, 20),
        ("FY2026E", "Teradata litigation", 29, 1, None, None),

        ("Q2 2026", "Acquisition-related charges", 92, 0, None, None),
        ("Q2 2026", "Restructuring", 7, 0, None, None),
        ("Q2 2026", "Teradata litigation", 0, 0, None, None),
        ("Q2 2026", "Equity securities gains/losses, net", -463, 0, None, None),

        ("Q1-Q2 2026", "Acquisition-related charges", 177, 0, None, None),
        ("Q1-Q2 2026", "Restructuring", 19, 0, None, None),
        ("Q1-Q2 2026", "Teradata litigation", 29, 0, None, None),
        ("Q1-Q2 2026", "Equity securities gains/losses, net", -504, 0, None, None),

        ("Q2 2025", "Acquisition-related charges", 94, 0, None, None),
        ("Q2 2025", "Restructuring", 18, 0, None, None),
        ("Q2 2025", "Teradata litigation", 0, 0, None, None),
        ("Q2 2025", "Equity securities gains/losses, net", -91, 0, None, None),

        ("Q1-Q2 2025", "Acquisition-related charges", 217, 0, None, None),
        ("Q1-Q2 2025", "Restructuring", 18, 0, None, None),
        ("Q1-Q2 2025", "Teradata litigation", 0, 0, None, None),
        ("Q1-Q2 2025", "Equity securities gains/losses, net", -299, 0, None, None),
    ]
    conn.executemany("""
        INSERT INTO non_ifrs_adjustments
        (period, adjustment_type, amount_eur_m, is_estimate, estimate_range_low, estimate_range_high)
        VALUES (?,?,?,?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
# 6. acquisitions (the M&A cadence question)
# ---------------------------------------------------------------
def load_acquisitions(conn):
    rows = [
        ("Reltio", "2026-03-27", "2026-05-07", 1076, "cash+share-based",
         "MDM/master data", "ATS", 25, -13, -8,
         "Closed within Q2; consideration = €979m cash + €96m share-based awards + €1m other liabilities. "
         "3% pre-existing equity stake remeasured to fair value (IFRS 3 stepped acquisition)."),
        ("Dremio", "2026-05-04", "2026-07-06", 500, "cash",
         "data lakehouse", None, None, None, None,
         "Closed AFTER Q2 close (July 6) — subsequent event, zero Q2 P&L contribution. "
         "Approx. €0.5bn cash consideration, majority of total."),
        ("Prior Labs", "2026-05-04", "2026-07-16", 400, "cash",
         "tabular foundation models", None, None, None, None,
         "Closed AFTER Q2 close (July 16) — subsequent event, zero Q2 P&L contribution. "
         "Approx. €0.4bn cash consideration, majority of total. Combined Dremio+Prior Labs "
         "dilution to FY2026 non-IFRS operating profit outlook: >€100m (outlook cut from "
         "€11.9-12.3bn to €11.8-12.2bn)."),
    ]
    conn.executemany("""
        INSERT INTO acquisitions
        (target_name, announced_date, closed_date, consideration_eur_m, consideration_type,
         strategic_category, segment_assigned, q2_revenue_contribution_eur_m,
         q2_operating_profit_contribution_ifrs_eur_m, q2_operating_profit_contribution_nonifrs_eur_m, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
# 7. customer_wins (tagged from Business Highlights section)
# ---------------------------------------------------------------
def load_customer_wins(conn):
    rise = ["ACCIONA", "AIRBUS", "City of Osnabrueck", "Electrolux", "Eli Lilly",
            "Gilead Sciences", "HARTING", "Hindustan Zinc", "The Humboldt University of Berlin",
            "JET", "Ørsted", "Samsonite Group", "Shell", "The Shoprite Group",
            "SIGNAL IDUNA", "SPAR (CH)", "Sun Pharma", "Vonovia"]
    grow = ["Gooroo Crédito", "Modular Data Centers", "Parloa", "Tarrant County", "Techem"]
    ai_data = ["AMADEUS", "BBC", "Booking.com", "GOL", "Oki Electric Industry",
               "PwC", "University Hospital Zurich", "Vale"]
    key_win = ["Birlasoft", "Capgemini", "Haier Group", "KaDeWe"]
    went_live = ["Döhler", "FANUC Europe", "Fonterra", "Natura Cosméticos", "SABESP", "TEAG"]

    rows = []
    for name in rise:
        rows.append((name, "RISE with SAP", "Q2 2026"))
    for name in grow:
        rows.append((name, "SAP GROW", "Q2 2026"))
    for name in ai_data:
        rows.append((name, "AI and data solutions", "Q2 2026"))
    for name in key_win:
        rows.append((name, "Key portfolio win", "Q2 2026"))
    for name in went_live:
        rows.append((name, "Went live", "Q2 2026"))

    conn.executemany("""
        INSERT INTO customer_wins (customer_name, category, period)
        VALUES (?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
# 8. headcount
# ---------------------------------------------------------------
def load_headcount(conn):
    def rows_for(period, data):
        out = []
        for func_area, (emea, americas, apj) in data.items():
            out.append((period, func_area, "EMEA", emea))
            out.append((period, func_area, "Americas", americas))
            out.append((period, func_area, "APJ", apj))
            out.append((period, func_area, "Total", emea + americas + apj))
        return out

    data_2026 = {
        "Cloud and software": (4684, 4573, 5496),
        "Services": (8298, 4600, 5842),
        "Research and development": (18741, 5883, 13685),
        "Sales and marketing": (12315, 10050, 5017),
        "General and administration": (4098, 1952, 1365),
        "Infrastructure": (3208, 1138, 1073),
    }
    data_2025 = {
        "Cloud and software": (4553, 4486, 5109),
        "Services": (8237, 4681, 5814),
        "Research and development": (18063, 5761, 13349),
        "Sales and marketing": (11694, 9793, 4981),
        "General and administration": (3903, 1910, 1343),
        "Infrastructure": (3123, 1152, 976),
    }

    rows = rows_for("6/30/2026", data_2026) + rows_for("6/30/2025", data_2025)
    conn.executemany("""
        INSERT INTO headcount (period, function_area, region, fte_count)
        VALUES (?,?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
# 9. key_kpis (top-line dashboard metrics)
# ---------------------------------------------------------------
def load_key_kpis(conn):
    rows = [
        # period, period_type, metric_name, ifrs_value, non_ifrs_value, unit
        ("Q2 2026", "quarter", "Current cloud backlog", None, 22929, "EUR_m"),
        ("Q2 2025", "quarter", "Current cloud backlog", None, 18052, "EUR_m"),
        ("Q2 2026", "quarter", "Cloud revenue", 6281, 6281, "EUR_m"),
        ("Q2 2025", "quarter", "Cloud revenue", 5130, 5130, "EUR_m"),
        ("Q2 2026", "quarter", "Cloud ERP Suite revenue", 5525, 5525, "EUR_m"),
        ("Q2 2025", "quarter", "Cloud ERP Suite revenue", 4422, 4422, "EUR_m"),
        ("Q2 2026", "quarter", "Total revenue", 9878, 9878, "EUR_m"),
        ("Q2 2025", "quarter", "Total revenue", 9027, 9027, "EUR_m"),
        ("Q2 2026", "quarter", "Gross profit", 7228, 7250, "EUR_m"),
        ("Q2 2025", "quarter", "Gross profit", 6620, 6643, "EUR_m"),
        ("Q2 2026", "quarter", "Operating profit", 2643, 2743, "EUR_m"),
        ("Q2 2025", "quarter", "Operating profit", 2456, 2568, "EUR_m"),
        ("Q2 2026", "quarter", "Operating margin", 26.8, 27.8, "pct"),
        ("Q2 2025", "quarter", "Operating margin", 27.2, 28.5, "pct"),
        ("Q2 2026", "quarter", "Profit after tax", 2209, 1828, "EUR_m"),
        ("Q2 2025", "quarter", "Profit after tax", 1749, 1747, "EUR_m"),
        ("Q2 2026", "quarter", "EPS basic", 1.89, 1.59, "EUR_per_share"),
        ("Q2 2025", "quarter", "EPS basic", 1.45, 1.50, "EUR_per_share"),
        ("Q2 2026", "quarter", "Net cash flow operating activities", 3153, None, "EUR_m"),
        ("Q2 2025", "quarter", "Net cash flow operating activities", 2577, None, "EUR_m"),
        ("Q2 2026", "quarter", "Free cash flow", None, 3002, "EUR_m"),
        ("Q2 2025", "quarter", "Free cash flow", None, 2357, "EUR_m"),

        ("Q1-Q2 2026", "half_year", "Current cloud backlog", None, 22929, "EUR_m"),
        ("Q1-Q2 2025", "half_year", "Current cloud backlog", None, 18052, "EUR_m"),
        ("Q1-Q2 2026", "half_year", "Cloud revenue", 12244, 12244, "EUR_m"),
        ("Q1-Q2 2025", "half_year", "Cloud revenue", 10124, 10124, "EUR_m"),
        ("Q1-Q2 2026", "half_year", "Total revenue", 19432, 19432, "EUR_m"),
        ("Q1-Q2 2025", "half_year", "Total revenue", 18040, 18040, "EUR_m"),
        ("Q1-Q2 2026", "half_year", "Operating profit", 5383, 5609, "EUR_m"),
        ("Q1-Q2 2025", "half_year", "Operating profit", 4789, 5024, "EUR_m"),
        ("Q1-Q2 2026", "half_year", "Operating margin", 27.7, 28.9, "pct"),
        ("Q1-Q2 2025", "half_year", "Operating margin", 26.5, 27.8, "pct"),
        ("Q1-Q2 2026", "half_year", "Profit after tax", 4155, 3830, "EUR_m"),
        ("Q1-Q2 2025", "half_year", "Profit after tax", 3545, 3428, "EUR_m"),
        ("Q1-Q2 2026", "half_year", "EPS basic", 3.55, 3.31, "EUR_per_share"),
        ("Q1-Q2 2025", "half_year", "EPS basic", 2.98, 2.94, "EUR_per_share"),
        ("Q1-Q2 2026", "half_year", "Effective tax rate", 27.8, 30.0, "pct"),
        ("Q1-Q2 2025", "half_year", "Effective tax rate", 28.7, 30.1, "pct"),
        ("Q1-Q2 2026", "half_year", "Net cash flow operating activities", 6666, None, "EUR_m"),
        ("Q1-Q2 2025", "half_year", "Net cash flow operating activities", 6357, None, "EUR_m"),
        ("Q1-Q2 2026", "half_year", "Free cash flow", None, 6250, "EUR_m"),
        ("Q1-Q2 2025", "half_year", "Free cash flow", None, 5939, "EUR_m"),
    ]
    conn.executemany("""
        INSERT INTO key_kpis (period, period_type, metric_name, ifrs_value, non_ifrs_value, unit)
        VALUES (?,?,?,?,?,?)
    """, rows)
    conn.commit()

# ---------------------------------------------------------------
def main():
    conn = get_conn()
    build_schema(conn)
    load_revenue_by_segment(conn)
    load_revenue_by_region(conn)
    load_cloud_revenue_breakdown(conn)
    load_opex(conn)
    load_non_ifrs_adjustments(conn)
    load_acquisitions(conn)
    load_customer_wins(conn)
    load_headcount(conn)
    load_key_kpis(conn)
    conn.close()
    print(f"Done. Database written to {DB_PATH}")

if __name__ == "__main__":
    main()
