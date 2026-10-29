"""Download SEC company facts for the bank valuation data preparation."""
import concurrent.futures
import json
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
TICKERS = 'JPM BAC C WFC GS MS USB PNC TFC COF SCHW STT NTRS FITB HBAN RF CFG KEY MTB ZION FHN EWBC WAL SSB PB'.split()
companies = {x['ticker']: x for x in json.loads((ROOT / 'sec-tickers.json').read_text()).values()}
target = ROOT / 'sec-data'
target.mkdir(exist_ok=True)

def download(ticker):
    company = companies[ticker]
    cik = str(company['cik_str']).zfill(10)
    url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
    request = urllib.request.Request(url, headers={'User-Agent': os.environ['SEC_USER_AGENT'], 'Accept-Encoding': 'identity'})
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = response.read()
    data = json.loads(payload)
    if int(data['cik']) != int(cik):
        raise ValueError(f'CIK mismatch for {ticker}')
    (target / f'{ticker}.json').write_bytes(payload)
    return f'{ticker}: {data["entityName"]} ({len(payload)} bytes)'

if __name__ == '__main__':
    if not os.environ.get('SEC_USER_AGENT'):
        raise SystemExit('Set SEC_USER_AGENT to a descriptive application name and valid contact email.')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for result in executor.map(download, TICKERS):
            print(result, flush=True)
