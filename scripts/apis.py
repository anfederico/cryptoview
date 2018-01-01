import sys
import time
import hmac
import hashlib
import urllib
import requests
import json
import base64

# Local Files
sys.path.append("..")
from scripts import models

key = 'XtF8ySScnn0mjtLTv1bw'
secret = '3VozjJ7qcUvTaLbK93CDAdYQDiox'

class Gemini:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def raw_balances(self):
        url = "https://api.sandbox.gemini.com/v1/balances"
        nonce = int(time.time() * 1000)
        message_json = json.dumps({"request": "/v1/balances", "nonce": nonce})
        message = base64.b64encode(message_json.encode())
        signature = hmac.new(self.api_secret.encode(), message, hashlib.sha384).hexdigest()
        headers = {'Content-Type': "text/plain",
                   'Content-Length': "0",
                   'X-GEMINI-APIKEY': self.api_key,
                   'X-GEMINI-PAYLOAD': message,
                   'X-GEMINI-SIGNATURE': signature,
                   'Cache-Control': "no-cache"}
        response = requests.request("POST", url, headers=headers)
        return response.json()

    def get_balances(self):
        E = models.Exchange('Gemini')
        raw = self.raw_balances()
        for t in raw:
            balance = float(t['available'])
            if balance > 0:
                ticker = t['currency'] + 'usd'
                try:
                    price = requests.get('https://api.gemini.com/v1/pubticker/{0}'.format(ticker)).json()['last']
                    E.tokens.append(models.Token(ticker, balance, 'Gemini', price=price))
                except KeyError:
                    E.tokens.append(models.Token(ticker, balance, 'Gemini'))
        return E


class Binance:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def raw_balances(self):
        session = requests.session()
        session.headers.update({'Accept': 'application/json','User-Agent': 'binance/python','X-MBX-APIKEY': self.api_key})
        kwargs = {'params': {'timestamp': int(time.time()*1000)}}
        query_string = urllib.parse.urlencode(kwargs['params'])
        apisign = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        kwargs['params']['signature'] = apisign
        response = getattr(session, 'get')('https://api.binance.com/api/v3/account', timeout=10, **kwargs)
        return response.json()['balances']

    def get_balances(self):
        E = models.Exchange('Binance')
        prices = requests.get('https://api.binance.com//api/v1/ticker/allPrices').json()
        prices = {i['symbol']: i['price'] for i in prices}
        raw = self.raw_balances()
        for t in raw:
            balance = float(t['free'])
            if balance > 0:
                ticker = t['asset']
                try:
                    price = prices['{0}BTC'.format(ticker)]
                    E.tokens.append(models.Token(ticker, balance, 'Binance', price=price))
                except KeyError:
                    E.tokens.append(models.Token(ticker, balance, 'Binance'))
        return E

class Bittrex:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def raw_balances(self):
        nonce = str(int(time.time()*1000))
        query_string = 'https://bittrex.com/api/v1.1/account/getbalances?'
        query_string += 'apikey=' + self.api_key + "&nonce=" + nonce + '&'
        apisign = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha512).hexdigest()
        response = requests.get(query_string, headers={"apisign": apisign})
        return response.json()['result']

    def get_balances(self):
        E = models.Exchange('Bittrex')
        prices = requests.get('https://bittrex.com/api/v1.1/public/getmarketsummaries').json()['result']
        prices = {i['MarketName']: i['Last'] for i in prices}
        raw = self.raw_balances()
        for t in raw:
            balance = float(t['Available'])
            if balance > 0:
                ticker = t['Currency']
                try:
                    price = prices['BTC-{0}'.format(ticker)]
                    E.tokens.append(models.Token(ticker, balance, 'Bittrex', price=price))
                except KeyError:
                    E.tokens.append(models.Token(ticker, balance, 'Bittrex'))
        return E

class Poloniex:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def raw_balances(self):
        args = {'command': 'returnCompleteBalances'}
        args['nonce'] = int(time.time()*1000000)
        data = urllib.parse.urlencode(args)
        sign = hmac.new(self.api_secret.encode('utf-8'), data.encode('utf-8'), hashlib.sha512)
        response = requests.post('https://poloniex.com/tradingApi', data=args,
                   headers={'Sign': sign.hexdigest(), 'Key': self.api_key}, timeout=10)
        return response.json()

    def get_balances(self):
        E = models.Exchange('Poloniex')
        raw = self.raw_balances()
        for t in raw:
            balance = float(raw[t]['available'])
            if balance > 0:
                value = float(raw[t]['btcValue'])
                ticker = t
                try:
                    E.tokens.append(models.Token(ticker, balance, 'Poloniex', value=value))
                except KeyError:
                    E.tokens.append(models.Token(ticker, balance, 'Poloniex'))                
        return E  

class Gdax:
    def __init__(self, api_key, api_secret, api_passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        
    def raw_balances(self):
        timestamp = str(time.time())
        message = timestamp+'GET/accounts/'
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.api_secret)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        response = requests.get('https://api.gdax.com/accounts/', headers={
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.api_passphrase})
        return response.json()

    def get_balances(self):
        E = models.Exchange('Poloniex')
        raw = self.raw_balances()
        for t in raw:
            balance = float(t['available'])
            if balance > 0:
                ticker = t['currency']
                try:
                    price = requests.get('https://api.gdax.com/products/{0}-BTC/ticker'.format(ticker)).json()['price']
                    E.tokens.append(models.Token(ticker, balance, 'Gdax', price=price))
                except KeyError:
                    E.tokens.append(models.Token(ticker, balance, 'Gdax'))
        return E
