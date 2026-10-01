# CreditLens eval report

Run: 2026-10-01 11:39 UTC | models: gemini-3.5-flash-lite, gemini-3.1-flash-lite, gemini-flash-lite-latest, gemma-4-31b-it, gemini-3.8-flash, gemini-flash-latest | embed: gemini-embedding-001

## Retrieval (gold evidence docs in top 6)

| Mode | Recall@6 | All gold found |
|---|---|---|
| bm25 | 1.0 | 22/22 |
| dense | 1.0 | 22/22 |
| hybrid | 1.0 | 22/22 |

## Answers

- n: 26
- errors: 0
- answer accuracy: 22/22
- abstention accuracy: 4/4
- false abstentions: 0
- citation support rate: 0.932
- uncited claims: 0
- median latency s: 1.9

| id | correct | abstained | claims supported | answer |
|---|---|---|---|---|
| sgp-1 | ✅ | False | 3/3 | The DSCR for Shree Ganesh Polymers Pvt Ltd in FY2024-25 was 1.62x. The credit policy requires a minimum DSCR of 1.25x on the latest audited  |
| sgp-2 | ✅ | False | 4/4 | The gap between GSTR-1 and GSTR-3B turnover is INR 2.3 crore, which is about 4.0% of GSTR-1 turnover [S1]. Supporting credit notes for INR 1 |
| sgp-3 | ✅ | False | 3/3 | The largest customer accounts for 41% of FY2024-25 revenue. The credit policy sets single-customer concentration above 40% of revenue as a w |
| sgp-4 | ✅ | False | 3/4 | The proposed term loan amount is INR 4.5 crore, which is above INR 3 crore [S1][S2]. Term loans above INR 3 crore require tangible collatera |
| sgp-5 | ✅ | False | 1/1 | The peak cash credit utilisation for Shree Ganesh Polymers Pvt Ltd was 96% in March 2025 [S1]. Peak cash credit utilisation reached 96% in M |
| sgp-6 | ✅ | False | 2/2 | There are no outward cheque returns (company's own cheques that bounced) [S1]. Under the credit policy, any outward cheque return for insuff |
| sgp-7 | ✅ | False | 2/2 | The promoter contribution is INR 1.2 crore [S1]. This promoter contribution constitutes 21% of the project cost of INR 5.7 crore [S1]. Promo |
| nlx-1 | ✅ | False | 3/3 | The provisional DSCR for Nimbus Logistics LLP for FY2024-25 is 0.94x [S1]. The credit policy mandates a minimum DSCR of 1.25x on the latest  |
| nlx-2 | ✅ | False | 3/3 | Yes, there were 2 instances of outward cheque returns for insufficient funds occurring in October 2024 and February 2025 [S1]. The total amo |
| nlx-3 | ✅ | False | 3/3 | The worst DPD on any facility in the last year is 32 days on the commercial vehicle loans [S1]. The 32 days-past-due occurred in January 202 |
| nlx-4 | ✅ | False | 2/3 | Debtor days for Nimbus Logistics LLP rose from 76 days in FY2023-24 to 108 days in FY2024-25. The increase of 32 days year-on-year exceeds t |
| nlx-5 | ✅ | False | 2/2 | Nimbus Logistics LLP has 6 credit enquiries in the last 6 months from different lenders [S1]. Having more than 4 credit enquiries in 6 month |
| nlx-6 | ✅ | False | 2/2 | The proposed security for the enhancement is the personal guarantee of both partners. No additional collateral is offered for the requested  |
| nlx-7 | ✅ | False | 2/2 | GSTR-3B was filed late in 5 of 12 months for Nimbus Logistics LLP [S1]. The longest delay for GSTR-3B filing was 34 days in December 2024 [S |
| afp-1 | ✅ | False | 3/3 | Related-party sales to Aarohi Distributors were INR 9.7 crore in FY2024-25, which represents 28% of revenue. Under the credit policy, relate |
| afp-2 | ✅ | False | 1/1 | Unsecured borrowing from three NBFCs increased from INR 1.2 crore to INR 5.3 crore within FY2024-25 [S1]. Unsecured NBFC borrowing grew from |
| afp-3 | ✅ | False | 3/3 | The debt to equity ratio for Aarohi Foods Pvt Ltd is 1.75x in FY2023-24 and 2.37x in FY2024-25. The policy requires a maximum debt-to-equity |
| afp-4 | ✅ | False | 2/2 | Revenue from operations for Aarohi Foods Pvt Ltd was 22.5 INR crore in FY2023-24 and 34.8 INR crore in FY2024-25 [S1]. Revenue grew 54.7% ye |
| afp-5 | ✅ | False | 2/4 | Term loans above INR 3 crore require tangible collateral cover of at least 1.25x the loan amount [S1]. The proposed term loan amount is INR  |
| afp-6 | ✅ | False | 2/2 | All 12 GSTR-3B returns were filed on time for Aarohi Foods Pvt Ltd in FY2024-25 [S1]. There are no demand notices for Aarohi Foods Pvt Ltd [ |
| pol-1 | ✅ | False | 1/1 | The credit policy mandates a minimum DSCR of 1.25x on the latest audited or provisional year [S1]. The minimum DSCR required by the credit p |
| pol-2 | ✅ | False | 4/4 | Nimbus Logistics LLP has a bureau rank of CMR-7 [S1]. Aarohi Foods Pvt Ltd has a bureau rank of CMR-4 [S2]. Shree Ganesh Polymers Pvt Ltd ha |
| na-1 | ✅ | True | 1/1 | The provided sources contain company net worth, debt, and promoter bureau details, but do not mention the promoter's personal net worth. Pro |
| na-2 | ✅ | True | 1/1 | The provided sources do not mention the interest rate at which the existing overdraft is priced. The interest rate of the existing overdraft |
| na-3 | ✅ | True | 0/0 | The provided sources do not contain revenue data for FY2022-23; financials are only provided for FY2023-24 and FY2024-25. |
| na-4 | ✅ | True | 0/0 | The provided sources do not contain information about the external credit rating from CRISIL for Shree Ganesh Polymers Pvt Ltd. |

## Credit memos

| Borrower | Recommendation | Rec OK | Risk flags found | Missed | Flag citations supported |
|---|---|---|---|---|---|
| sgp | Proceed with conditions | ✅ | 2/2 | - | 6/6 |
| nlx | Decline | ✅ | 6/7 | collateral | 7/7 |
| afp | Decline | ✅ | 4/5 | collateral | 6/6 |

Models that served answers (free-tier rotation): gemini-3.5-flash-lite (26)
