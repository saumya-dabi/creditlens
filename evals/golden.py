"""Golden eval set. `must` = strings that must appear in the answer; `gold` = chunk-file stems that hold the evidence.
answerable=False items test abstention (the data is genuinely not in the corpus)."""

QA = [
    # Shree Ganesh Polymers
    {"id": "sgp-1", "company": "sgp", "q": "What was the DSCR in FY2024-25 and does it meet policy?", "must": ["1.62"], "gold": ["sgp_financials", "lending_policy"]},
    {"id": "sgp-2", "company": "sgp", "q": "How big is the gap between GSTR-1 and GSTR-3B turnover and how much of it is unexplained?", "must": ["2.3", "0.7"], "gold": ["sgp_gst"]},
    {"id": "sgp-3", "company": "sgp", "q": "Is customer concentration a concern?", "must": ["41%"], "gold": ["sgp_financials", "lending_policy"]},
    {"id": "sgp-4", "company": "sgp", "q": "Does the collateral cover the proposed term loan as per policy?", "must": ["11.2", "4.5"], "gold": ["sgp_request", "lending_policy"]},
    {"id": "sgp-5", "company": "sgp", "q": "What was peak cash credit utilisation?", "must": ["96%"], "gold": ["sgp_bank"]},
    {"id": "sgp-6", "company": "sgp", "q": "Any outward cheque bounces?", "must": ["none|no outward|no cheque"], "gold": ["sgp_bank"]},
    {"id": "sgp-7", "company": "sgp", "q": "How much promoter contribution is there in the project?", "must": ["1.2", "21%"], "gold": ["sgp_request"]},
    # Nimbus Logistics
    {"id": "nlx-1", "company": "nlx", "q": "What is the DSCR and does Nimbus pass the minimum DSCR rule?", "must": ["0.94", "1.25"], "gold": ["nlx_financials", "lending_policy"]},
    {"id": "nlx-2", "company": "nlx", "q": "Were there any outward cheque returns for insufficient funds?", "must": ["2", "0.14"], "gold": ["nlx_bank"]},
    {"id": "nlx-3", "company": "nlx", "q": "What is the worst DPD on any facility in the last year?", "must": ["32"], "gold": ["nlx_bureau"]},
    {"id": "nlx-4", "company": "nlx", "q": "How have debtor days moved?", "must": ["76", "108"], "gold": ["nlx_financials"]},
    {"id": "nlx-5", "company": "nlx", "q": "How many credit enquiries in the last 6 months?", "must": ["6"], "gold": ["nlx_bureau"]},
    {"id": "nlx-6", "company": "nlx", "q": "What collateral is offered for the enhancement?", "must": ["personal guarantee"], "gold": ["nlx_request"]},
    {"id": "nlx-7", "company": "nlx", "q": "How many months was GSTR-3B filed late?", "must": ["5"], "gold": ["nlx_gst"]},
    # Aarohi Foods
    {"id": "afp-1", "company": "afp", "q": "How large are related-party sales as a share of revenue?", "must": ["28%"], "gold": ["afp_financials"]},
    {"id": "afp-2", "company": "afp", "q": "How fast did unsecured NBFC borrowing grow?", "must": ["1.2", "5.3"], "gold": ["afp_bureau"]},
    {"id": "afp-3", "company": "afp", "q": "What is the debt to equity ratio and is it within policy?", "must": ["2.37"], "gold": ["afp_financials", "lending_policy"]},
    {"id": "afp-4", "company": "afp", "q": "What was revenue growth in FY2024-25?", "must": ["54.7%"], "gold": ["afp_financials"]},
    {"id": "afp-5", "company": "afp", "q": "Does the plant valuation cover the INR 6 crore term loan at 1.25x?", "must": ["7.4"], "gold": ["afp_request", "lending_policy"]},
    {"id": "afp-6", "company": "afp", "q": "Is GST filing discipline good?", "must": ["on time"], "gold": ["afp_gst"]},
    # Cross-company / policy
    {"id": "pol-1", "company": None, "q": "What is the minimum DSCR required by the credit policy?", "must": ["1.25"], "gold": ["lending_policy"]},
    {"id": "pol-2", "company": None, "q": "Which borrower has the highest bureau CMR rank (worst)?", "must": ["Nimbus", "CMR-7"], "gold": ["nlx_bureau"]},
    # Unanswerable: not in corpus
    {"id": "na-1", "company": "sgp", "q": "What is the promoter's personal net worth?", "answerable": False, "gold": []},
    {"id": "na-2", "company": "nlx", "q": "What interest rate is the existing overdraft priced at?", "answerable": False, "gold": []},
    {"id": "na-3", "company": "afp", "q": "What was revenue in FY2022-23?", "answerable": False, "gold": []},
    {"id": "na-4", "company": "sgp", "q": "What is the company's external credit rating from CRISIL?", "answerable": False, "gold": []},
]

# Expected outcome of the pre-screen memo (analyst ground truth)
MEMO = {
    "sgp": {"recommendation": ["Proceed with conditions", "Proceed"],
            "must_flag": ["gst", "concentration"]},
    "nlx": {"recommendation": ["Decline", "Refer to credit committee"],
            "must_flag": ["dscr", "debt", "cheque", "dpd", "enquir", "debtor", "collateral"]},
    "afp": {"recommendation": ["Refer to credit committee", "Proceed with conditions", "Decline"],
            "must_flag": ["dscr", "debt", "related", "unsecured", "collateral"]},
}
