import copy
import requests
import sys

# Local Files
sys.path.append("..")
from scripts import settings, apis, models

def parser(balances, exchange):
    E = models.Exchange(exchange)
    if exchange is 'poloniex':
        for token in balances:
            summary = balances[token]
            if float(summary['available']) > 0:
                E.tokens.append(models.Token(token, summary['available'], exchange, value=summary['btcValue']))

    elif exchange is 'gdax':
        for token in balances:
            if float(token['available']) > 0:
                quote = requests.get('https://api.gdax.com/products/{0}-BTC/ticker'.format(token['currency'])).json()
                try:
                    E.tokens.append(models.Token(token['currency'], token['available'], exchange, price=quote['price']))
                except KeyError:
                    E.tokens.append(models.Token(token['currency'], token['available'], exchange))

    elif exchange is 'bittrex':
        for token in balances['result']:
            if float(token['Available']) > 0:
                quote = requests.get('https://bittrex.com/api/v1.1/public/getticker?market=BTC-{0}'.format(token['Currency'])).json()
                try:
                    E.tokens.append(models.Token(token['Currency'], token['Available'], exchange, price=quote['result']['Last']))
                except TypeError:
                    E.tokens.append(models.Token(token['Currency'], token['Available'], exchange))
    return E
 
def refresh_positions(exchanges=[]):
    E = []
    if 'poloniex' in exchanges:
        poloniex = apis.Poloniex_Init(settings.poloniex_key, settings.poloniex_secret)
        balances = poloniex('returnCompleteBalances')
        E.append(parser(balances, 'poloniex'))

    if 'gdax' in exchanges:
        gdax = apis.Gdax_Init(settings.gdax_key, settings.gdax_secret, settings.gdax_passphrase)
        balances = gdax('accounts')
        E.append(parser(balances, 'gdax'))

    if 'bittrex' in exchanges:
        bittrex = apis.Bittrex_Init(settings.bittrex_key, settings.bittrex_secret)
        balances = bittrex('getbalances')
        E.append(parser(balances, 'bittrex'))

    Agg = E[0]
    for i in range(1, len(E)):
        Agg += E[i]
        
    return Agg.positions()