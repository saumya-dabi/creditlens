"""Builds the synthetic credit-file corpus used by CreditLens.

All companies, people and numbers are FICTIONAL. They are written to look like
what an Indian SME lender's credit analyst sees: audited financials, GST return
summaries, bank-statement analysis, bureau report and a loan request note.
Risk signals are planted deliberately so the eval set can check them.
"""
from pathlib import Path

OUT = Path(__file__).parent / "docs"

DOCS = {
# ---------------------------------------------------------------- Company A
"sgp_financials.md": """# Shree Ganesh Polymers Pvt Ltd — Audited Financial Summary
Company: Shree Ganesh Polymers Pvt Ltd | CIN (fictional): U25209PN2011PTC000001 | Location: Chakan MIDC, Pune | Business: injection-moulded automotive plastic components | Auditor: R. Kulkarni & Associates

## Profit and loss (INR crore)
| Item | FY2023-24 | FY2024-25 |
|---|---|---|
| Revenue from operations | 48.6 | 56.2 |
| EBITDA | 6.3 | 7.6 |
| EBITDA margin | 13.0% | 13.5% |
| Finance cost | 1.4 | 1.5 |
| Depreciation | 1.9 | 2.1 |
| Profit after tax | 2.2 | 2.9 |

Revenue grew 15.6% year on year, driven by a new supply contract with a two-wheeler OEM that contributed INR 6.1 crore in FY2024-25.

## Balance sheet (INR crore, 31 March)
| Item | FY2023-24 | FY2024-25 |
|---|---|---|
| Net worth | 17.8 | 20.7 |
| Total debt | 14.2 | 15.1 |
| Debt to equity | 0.80x | 0.73x |
| Trade receivables | 9.1 | 10.8 |
| Inventory | 5.4 | 6.0 |
| Current ratio | 1.42x | 1.48x |

## Coverage and working capital
- DSCR for FY2024-25: 1.62x (FY2023-24: 1.48x).
- Interest coverage (EBITDA / finance cost) for FY2024-25: 5.1x.
- Debtor days FY2024-25: 70 days (FY2023-24: 68 days).
- Top customer concentration: the largest customer accounts for 41% of FY2024-25 revenue.

## Auditor remarks
Unqualified audit opinion for both years. The auditor noted one emphasis-of-matter item: a pending excise dispute of INR 0.35 crore from 2016, with a provision of INR 0.10 crore.
""",

"sgp_gst.md": """# Shree Ganesh Polymers Pvt Ltd — GST Return Analysis (FY2024-25)
GSTIN (fictional): 27AAACS0001A1Z5 | State: Maharashtra

## Turnover reconciliation
- Turnover declared in GSTR-1 (outward supplies): INR 57.9 crore.
- Turnover on which tax was paid in GSTR-3B: INR 55.6 crore.
- Gap between GSTR-1 and GSTR-3B: INR 2.3 crore (about 4.0% of GSTR-1 turnover).
- Management explanation: credit notes for returned stock issued in Q4 were reported in GSTR-1 of the following month. Supporting credit notes for INR 1.6 crore were provided; INR 0.7 crore remains unexplained.

## Filing discipline
- GSTR-3B filed late in 2 of 12 months (August 2024 by 6 days, January 2025 by 11 days).
- No GST demand notices outstanding as of the analysis date.

## Input tax credit
ITC claimed in GSTR-3B matched GSTR-2B within 1.2% for the year.
""",

"sgp_bank.md": """# Shree Ganesh Polymers Pvt Ltd — Bank Statement Analysis
Period: April 2024 to March 2025 | Primary account: cash credit account with a public-sector bank, sanctioned limit INR 6.0 crore

## Utilisation
- Average cash-credit utilisation: 74% of the sanctioned limit.
- Peak utilisation: 96% in March 2025.
- No overdrawing beyond the sanctioned limit during the period.

## Credits and bounces
- Total credits in the period: INR 58.4 crore, consistent with reported revenue.
- Inward cheque returns (customer cheques that bounced): 1 instance, INR 0.08 crore, re-presented and cleared.
- Outward cheque returns (company's own cheques that bounced): none.

## EMI behaviour
All 12 EMIs on the term loan were debited on time.
""",

"sgp_bureau.md": """# Shree Ganesh Polymers Pvt Ltd — Commercial Bureau Report Summary
Report date: 15 May 2025 | Bureau rank (fictional scale 1 best to 10 worst): CMR-3

## Active facilities
| Lender type | Facility | Sanctioned (INR cr) | Outstanding (INR cr) | Max DPD (12 months) |
|---|---|---|---|---|
| Public-sector bank | Cash credit | 6.0 | 4.4 | 0 |
| Public-sector bank | Term loan (machinery) | 8.0 | 5.9 | 0 |
| NBFC | Equipment loan | 2.5 | 1.6 | 0 |

## Promoter bureau
Promoter Mr. Ajay Deshmukh (fictional) has a consumer bureau score of 782 with no delinquencies. No wilful-defaulter or suit-filed records.
""",

"sgp_request.md": """# Shree Ganesh Polymers Pvt Ltd — Loan Request Note
Requested facility: term loan of INR 4.5 crore for a new 350-tonne moulding line. Proposed tenor: 5 years with 6 months moratorium. Proposed security: hypothecation of the new machinery plus extension of the existing equitable mortgage on the Chakan factory (valuation INR 11.2 crore, May 2025).
Promoter contribution: INR 1.2 crore (21% of project cost of INR 5.7 crore).
Projected incremental revenue from the new line: INR 9.0 crore per year from FY2026-27.
""",

# ---------------------------------------------------------------- Company B
"nlx_financials.md": """# Nimbus Logistics LLP — Financial Summary
Entity: Nimbus Logistics LLP | LLPIN (fictional): AAB-0002 | Location: Bhiwandi, Thane | Business: B2B road freight and warehousing for FMCG distributors | Accounts: audited FY2023-24, provisional FY2024-25

## Profit and loss (INR crore)
| Item | FY2023-24 | FY2024-25 (provisional) |
|---|---|---|
| Revenue from operations | 31.4 | 33.0 |
| EBITDA | 3.8 | 2.6 |
| EBITDA margin | 12.1% | 7.9% |
| Finance cost | 1.6 | 2.0 |
| Profit after tax | 0.9 | 0.1 |

Margin compression is attributed to diesel cost increases and the loss of a rate-revision clause with the largest client.

## Balance sheet (INR crore, 31 March)
| Item | FY2023-24 | FY2024-25 (provisional) |
|---|---|---|
| Partners' capital | 6.1 | 5.7 |
| Total debt | 11.9 | 14.4 |
| Debt to equity | 1.95x | 2.53x |
| Trade receivables | 6.5 | 9.8 |
| Current ratio | 1.12x | 0.96x |

## Coverage and working capital
- DSCR for FY2024-25 (provisional): 0.94x (FY2023-24: 1.21x).
- Debtor days rose from 76 days in FY2023-24 to 108 days in FY2024-25.
- Partners withdrew INR 0.5 crore in FY2024-25 despite near-zero profit.
""",

"nlx_gst.md": """# Nimbus Logistics LLP — GST Return Analysis (FY2024-25)
GSTIN (fictional): 27AAAFN0002B1Z2 | State: Maharashtra

## Turnover reconciliation
- Turnover in GSTR-1: INR 33.4 crore. Turnover in GSTR-3B: INR 33.1 crore. Gap: 0.9%, within normal range.

## Filing discipline
- GSTR-3B filed late in 5 of 12 months; the longest delay was 34 days (December 2024).
- Late fees and interest paid: INR 0.04 crore.
- One GST demand notice of INR 0.22 crore (FY2021-22, ITC mismatch) is under appeal.
""",

"nlx_bank.md": """# Nimbus Logistics LLP — Bank Statement Analysis
Period: April 2024 to March 2025 | Overdraft account with a private bank, sanctioned limit INR 3.5 crore

## Utilisation
- Average overdraft utilisation: 97% of the limit.
- The account was overdrawn beyond the sanctioned limit on 9 occasions, for a total of 23 days.

## Credits and bounces
- Total credits: INR 30.2 crore, about 8% below reported revenue.
- Inward cheque returns: 3 instances totalling INR 0.31 crore, all from the same distributor client (Vashi Traders, fictional).
- Outward cheque returns: 2 instances, both for insufficient funds (October 2024 and February 2025), totalling INR 0.14 crore.

## EMI behaviour
Two EMIs on the vehicle loans were debited 4 and 9 days late.
""",

"nlx_bureau.md": """# Nimbus Logistics LLP — Commercial Bureau Report Summary
Report date: 20 May 2025 | Bureau rank (fictional scale 1 best to 10 worst): CMR-7

## Active facilities
| Lender type | Facility | Sanctioned (INR cr) | Outstanding (INR cr) | Max DPD (12 months) |
|---|---|---|---|---|
| Private bank | Overdraft | 3.5 | 3.4 | 0 |
| NBFC | Commercial vehicle loans (14 trucks) | 7.8 | 5.6 | 32 |
| Fintech lender | Unsecured business loan | 1.0 | 0.8 | 0 |

The 32 days-past-due on the commercial vehicle loans was in January 2025 and was regularised in February 2025.

## Enquiries
6 credit enquiries in the last 6 months from different lenders, which suggests the borrower is shopping for credit.

## Partner bureau
Designated partner Mr. Rohit Sawant (fictional) has a consumer bureau score of 694 with one credit-card account reported 60+ DPD in 2023.
""",

"nlx_request.md": """# Nimbus Logistics LLP — Loan Request Note
Requested facility: enhancement of the overdraft limit from INR 3.5 crore to INR 5.0 crore, plus a new working-capital term loan of INR 1.5 crore. Purpose stated: to fund receivables from a new e-commerce warehousing contract.
Proposed security: personal guarantee of both partners; no additional collateral offered.
""",

# ---------------------------------------------------------------- Company C
"afp_financials.md": """# Aarohi Foods Pvt Ltd — Audited Financial Summary
Company: Aarohi Foods Pvt Ltd | CIN (fictional): U15400MP2018PTC000003 | Location: Sanwer Road, Indore | Business: packaged namkeen and ready-to-eat snacks, sold through distributors and quick-commerce platforms

## Profit and loss (INR crore)
| Item | FY2023-24 | FY2024-25 |
|---|---|---|
| Revenue from operations | 22.5 | 34.8 |
| EBITDA | 2.5 | 4.0 |
| EBITDA margin | 11.1% | 11.5% |
| Finance cost | 0.9 | 1.6 |
| Profit after tax | 0.8 | 1.1 |

Revenue grew 54.7% year on year. Quick-commerce channels contributed 19% of FY2024-25 revenue, up from 6%.

## Balance sheet (INR crore, 31 March)
| Item | FY2023-24 | FY2024-25 |
|---|---|---|
| Net worth | 5.6 | 6.7 |
| Total debt | 9.8 | 15.9 |
| Debt to equity | 1.75x | 2.37x |
| Trade receivables | 3.9 | 6.6 |
| Inventory | 2.8 | 4.9 |
| Current ratio | 1.21x | 1.15x |

## Coverage
- DSCR for FY2024-25: 1.18x (FY2023-24: 1.31x).
- Interest coverage FY2024-25: 2.5x.

## Related-party transactions
Sales to Aarohi Distributors (fictional), a firm owned by the promoter's brother, were INR 9.7 crore in FY2024-25, which is 28% of revenue. Receivables from this related party were INR 2.9 crore at year end, 44% of total receivables.

## Auditor remarks
Unqualified opinion. The auditor flagged that related-party sales were priced at a 6% discount to the average distributor price.
""",

"afp_gst.md": """# Aarohi Foods Pvt Ltd — GST Return Analysis (FY2024-25)
GSTIN (fictional): 23AAJCA0003C1Z9 | State: Madhya Pradesh

## Turnover reconciliation
- GSTR-1 turnover: INR 35.1 crore. GSTR-3B turnover: INR 34.9 crore. Gap: 0.6%.

## Filing discipline
All 12 GSTR-3B returns filed on time. No demand notices.
""",

"afp_bank.md": """# Aarohi Foods Pvt Ltd — Bank Statement Analysis
Period: April 2024 to March 2025 | Cash credit with a small finance bank, limit INR 4.0 crore

## Utilisation
- Average utilisation: 88%; peak 100% in November 2024 (festive inventory build-up).
- No overdrawing beyond limit.

## Credits and bounces
- Total credits: INR 36.0 crore.
- Inward cheque returns: none. Outward cheque returns: none.
- Quick-commerce platform settlements arrive weekly; 22% of credits by value came from two platforms.
""",

"afp_bureau.md": """# Aarohi Foods Pvt Ltd — Commercial Bureau Report Summary
Report date: 2 June 2025 | Bureau rank (fictional scale 1 best to 10 worst): CMR-4

## Active facilities
| Lender type | Facility | Sanctioned (INR cr) | Outstanding (INR cr) | Max DPD (12 months) |
|---|---|---|---|---|
| Small finance bank | Cash credit | 4.0 | 3.5 | 0 |
| Small finance bank | Term loan (plant) | 7.0 | 6.1 | 0 |
| NBFC | Unsecured business loans (3 lenders) | 6.5 | 5.3 | 0 |

Unsecured borrowing from three NBFCs increased from INR 1.2 crore to INR 5.3 crore within FY2024-25.

## Promoter bureau
Promoter Ms. Kavya Jain (fictional) has a consumer bureau score of 741 with no delinquencies.
""",

"afp_request.md": """# Aarohi Foods Pvt Ltd — Loan Request Note
Requested facility: term loan of INR 6.0 crore for a second production line and a cold-storage unit, plus cash-credit enhancement from INR 4.0 crore to INR 6.0 crore.
Proposed security: hypothecation of new assets and an equitable mortgage on the Indore plant (valuation INR 7.4 crore).
Management projects FY2025-26 revenue of INR 52 crore.
""",

# ---------------------------------------------------------------- Policy
"lending_policy.md": """# Credit Policy Extract — SME Term and Working-Capital Lending (fictional lender)

## Hard eligibility rules
- Minimum DSCR of 1.25x on the latest audited or provisional year.
- Maximum debt-to-equity of 2.0x after the proposed loan.
- No DPD above 30 days on any facility in the last 12 months, unless regularised and explained with evidence.
- Any outward cheque return for insufficient funds in the last 6 months requires credit-committee approval.

## Watch-list triggers (do not auto-decline, but must be addressed in the credit memo)
- GSTR-1 vs GSTR-3B turnover gap above 3%.
- GSTR-3B filed late in more than 3 months of the year.
- Related-party sales above 20% of revenue.
- Single-customer concentration above 40% of revenue.
- More than 4 credit enquiries in 6 months.
- Debtor days above 90 or increasing by more than 20 days year on year.
- Unsecured borrowing growing more than 2x in a year.

## Collateral
Term loans above INR 3 crore require tangible collateral cover of at least 1.25x the loan amount.
""",
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in DOCS.items():
        (OUT / name).write_text(text.strip() + "\n")
    print(f"wrote {len(DOCS)} docs to {OUT}")
