import requests
import datetime

# Local Files
from scripts import mongio

def get_btc_price():
    btc = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/').json()
    return float(btc[0]['price_usd'])

def update_equity(account):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    positions = mongio.load(account, 'positions')
    btc = sum([p['Value'] for p in positions])
    usd = btc*get_btc_price()
    equity = mongio.load(account, 'equity')
    equity['btc'][now] = round(btc, 3) 
    equity['usd'][now] = round(usd, 3)
    mongio.save(account, 'equity', equity)