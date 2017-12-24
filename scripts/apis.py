import time
import hmac
import hashlib
import urllib
import requests
import json
import base64

class Bittrex_Init:
    def __init__(self, api_key='', api_secret=''):
        self.api_key = api_key
        self.api_secret = api_secret

    def __call__(self, command, args={}):
        nonce = str(int(time.time()*1000))
        method_set = 'account'
        request_url = ('https://bittrex.com/api/v1.1/%s/' % method_set) + command + '?'
        request_url += 'apikey=' + self.api_key + "&nonce=" + nonce + '&'
        request_url += urllib.urlencode(args)
        apisign = hmac.new(self.api_secret.encode(), request_url.encode(), hashlib.sha512).hexdigest()
        return requests.get(request_url, headers={"apisign": apisign}).json()

class Gdax_Init:
    def __init__(self, key, secret, passphrase, api_url="https://api.gdax.com"):
        self.url = api_url.rstrip('/')
        self.auth = Gdax_Auth(key, secret, passphrase)

    def __call__(self, command, arg=""):
        r = requests.get(self.url + '/'+ command+ '/' + arg, auth=self.auth, timeout=30)
        return r.json()        

class Gdax_Auth:
    def __init__(self, key, secret, passphrase):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        message = message.encode('ascii')
        hmac_key = base64.b64decode(self.secret)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'Content-Type': 'Application/JSON',
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.key,
            'CB-ACCESS-PASSPHRASE': self.passphrase})
        return request

class Poloniex_Init:
    def __init__(self, key="", secret="", timeout=30):
        self.key = key
        self.secret = secret
        self.timeout = timeout
        self.nonce = int(time.time()*1000000)

    def __call__(self, command, args={}):
        args['command'] = command
        args['nonce'] = self.nonce
        try:
            data = urllib.urlencode(args)
            sign = hmac.new(self.secret.encode('utf-8'), data.encode('utf-8'), hashlib.sha512)
            response = requests.post('https://poloniex.com/tradingApi', data=args,
                                      headers={'Sign': sign.hexdigest(), 'Key': self.key},
                                      timeout=self.timeout)
        except Exception as exception: raise exception
        finally: self.nonce += 1
        try: return json.loads(response.text, parse_float=unicode)
        except NameError: return json.loads(response.text, parse_float=str)