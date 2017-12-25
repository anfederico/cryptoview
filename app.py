from flask  import Flask, redirect, url_for, render_template, request

import threading
import schedule
import signal
import json
import os
import time

# Locals
from scripts import mongio, workers, settings

app = Flask(__name__)

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
    positions = workers.refresh_positions(settings.exchanges)
    mongio.save(settings.mongo_portfolio, 'positions', positions)
    positions = mongio.load(settings.mongo_portfolio, 'positions')
    return json.dumps({'success': True, 'positions': positions})

# ======== Main ============================================================== #

if __name__ == "__main__":
    app.run()
