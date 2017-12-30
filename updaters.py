import requests
import datetime
import schedule
import time

# Local Files
from scripts import mongio, settings

def get_btc_price():
    btc = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/').json()
    return float(btc[0]['price_usd'])

def update_equity():
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    print('{0} | Updating equity'.format(now))
    positions = mongio.load(settings.mongo_portfolio, 'positions')
    btc = sum([p['Value'] for p in positions])
    usd = btc*get_btc_price()
    equity = mongio.load(settings.mongo_portfolio, 'equity')
    equity['btc'][now] = round(btc, 3) 
    equity['usd'][now] = round(usd, 3)
    mongio.save(settings.mongo_portfolio, 'equity', equity)

if __name__ == "__main__":
    print('Starting scheduler...')
    schedule.every(15).minutes.do(update_equity)
    while True:
        schedule.run_pending()
        time.sleep(1)