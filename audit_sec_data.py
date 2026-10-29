"""Summarize SEC company-facts coverage; missing tags are not treated as zero."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAGS = {
    'assets': ['Assets'],
    'deposits': ['Deposits'],
    'equity': ['StockholdersEquity'],
    'financing_receivables_gross': ['FinancingReceivableExcludingAccruedInterestBeforeAllowanceForCreditLoss'],
    'financing_receivables_net': ['FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss', 'LoansAndLeasesReceivableNetReportedAmount', 'LoansAndLeasesReceivableNetOfDeferredIncome'],
    'net_interest_income': ['InterestIncomeExpenseNet'],
    'noninterest_income': ['NoninterestIncome'],
    'noninterest_expense': ['NoninterestExpense'],
    'net_income': ['NetIncomeLoss'],
    'diluted_eps': ['EarningsPerShareDiluted'],
    'diluted_shares': ['WeightedAverageNumberOfDilutedSharesOutstanding'],
    'goodwill': ['Goodwill'],
    'risk_weighted_assets': ['RiskWeightedAssets'],
}

rows = []
for path in sorted((ROOT / 'sec-data').glob('*.json')):
    data = json.loads(path.read_text(encoding='utf-8'))
    facts = data.get('facts', {}).get('us-gaap', {})
    row = {'ticker': path.stem, 'cik': data['cik'], 'entity_name': data['entityName']}
    for metric, tags in TAGS.items():
        entries = [(tag, item) for tag in tags for values in facts.get(tag, {}).get('units', {}).values()
                   for item in values if item.get('form') in ('10-Q', '10-K') and item.get('end', '') >= '2025-01-01']
        entries.sort(key=lambda pair: (pair[1]['end'], pair[1].get('filed', '')), reverse=True)
        row[metric] = f"{entries[0][0]} ({entries[0][1]['end']})" if entries else ''
    rows.append(row)
with (ROOT / 'sec-data-coverage.csv').open('w', newline='', encoding='utf-8') as output:
    writer = csv.DictWriter(output, fieldnames=['ticker', 'cik', 'entity_name', *TAGS])
    writer.writeheader()
    writer.writerows(rows)
print(f'Audited {len(rows)} companies; blank cells mean no recent fact for the selected tags.')
