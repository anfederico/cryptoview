import requests
import copy

def get_performances():
    data = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
    p = {}
    for ticker in data:
        t = dict(ticker)
        p[t['symbol']] = {'daily': t['percent_change_24h'],
                          'weekly': t['percent_change_7d']}
    return p

class Exchange:
    def __init__(self, name):
        self.name = name
        self.tokens = []

    def __str__(self):
        string = "Exchange: {0}\n".format(self.name)
        for token in self.tokens:
            string += "{0} {1} = {2} BTC\n".format(token.balance, token.name, token.value)
        return string

    def __add__(self, other):
        new = copy.deepcopy(self)
        new.name += "/"+other.name
        for t1 in new.tokens:
            for t2 in other.tokens:
                if t1 == t2:
                    t1 += t2                
        new.tokens += [t for t in other.tokens if t not in new.tokens]
        return new

    def __radd__(self, other):
        if other is int(0):
            return self
        else:
            return self.__add__(other)

    def positions(self):
        p = get_performances()
        self.tokens.sort(key=lambda t: t.value, reverse=True)
        total_btc = sum([token.value for token in self.tokens])
        positions = []
        for token in self.tokens:

            # Ignore dust
            if token.value < 0.001:
                continue

            try:
                positions.append({'Token'      : token.name, 
                                  'Balance'    : round(token.balance, 2),
                                  'Value'      : round(token.value, 5),
                                  'Allocation' : round(100*token.value/total_btc, 3),
                                  'Daily'      : p[token.name]['daily'],
                                  'Weekly'     : p[token.name]['weekly'],
                                  'Exchanges'  : "/".join(token.exchanges)})
            except KeyError as e:
                positions.append({'Token'      : token.name, 
                                  'Balance'    : round(token.balance, 2),
                                  'Value'      : round(token.value, 5),
                                  'Allocation' : round(100*token.value/total_btc, 3),
                                  'Daily'      : '--',
                                  'Weekly'     : '--',
                                  'Exchanges'  : "/".join(token.exchanges)})
        return positions

class Token:
    def __init__(self, name, balance, exchange, value=None, price=None):
        self.name = name.upper()
        self.balance = float(balance)
        self.exchanges = [exchange]
        if name == "BTC":
            self.value = float(balance)
            return
        if name == "USD" or name == "USDT":
            self.value = 0
            return
        try:
            self.value = float(value)
        except TypeError:
            try:
                self.value = float(price)*float(balance)
            except TypeError:
                self.value = 0

    def __str__(self):
        return "{0} {1} = {2} BTC".format(self.balance, self.name, self.value)

    def __eq__(self, other):
        return self.name == other.name

    def __add__(self, other):
        self.balance += other.balance
        self.value += other.value
        self.exchanges += other.exchanges
        return self
