from flask  import Flask, redirect, url_for, render_template, request

import threading
import signal
import json
import os
import time

# Locals
from scripts import mongio, apis, settings

app = Flask(__name__)

# ======== Tasks =========================================================== #
def refresh_positions(exchanges):
    E = []
    for exchange in exchanges:
        e = getattr(apis, exchange.title())
        key = getattr(settings, '{0}_key'.format(exchange))
        secret = getattr(settings, '{0}_secret'.format(exchange))
        try:
            passphrase = getattr(settings, '{0}_passphrase'.format(exchange))
            E.append(e(key, secret, passphrase).get_balances())
        except AttributeError:
            E.append(e(key, secret).get_balances())
    return sum(E).positions()

# ======== Routing =========================================================== #

@app.route('/', methods=['GET'])
def index():
    if 'positions' not in mongio.db.collection_names():
        mongio.db.create_collection('positions')
        mongio.save(settings.mongo_portfolio, 'positions', [])
        mongio.save(settings.mongo_portfolio, 'equity', {'btc':{}, 'usd':{}})

    positions = mongio.load(settings.mongo_portfolio, 'positions')
    equity = mongio.load(settings.mongo_portfolio, 'equity')
    return render_template('index.html', p=positions, e=equity)

@app.route('/refresh', methods=['POST'])
def refresh():
    positions = refresh_positions(settings.exchanges)
    mongio.save(settings.mongo_portfolio, 'positions', positions)
    positions = mongio.load(settings.mongo_portfolio, 'positions')
    return json.dumps({'success': True, 'positions': positions})

# ======== Main ============================================================== #

if __name__ == "__main__":
    app.run()