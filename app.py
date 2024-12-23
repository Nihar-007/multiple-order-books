from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests

app = Flask(__name__)

def get_binance_order_book(coin_id):
    url = f"https://www.binance.com/api/v3/depth?symbol={coin_id}USDT&limit=1000"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

@app.route('/', methods=['GET', 'POST'])
def home():
    coin_id = None

    if request.method == 'POST':
        coin_id = request.form.get('coin_id')
        coin_id = coin_id.upper()
        if coin_id:
            return redirect(url_for('order_book',coin_id=coin_id))
    
    coins = ["DOGE","ETH","SHIB","BTC","TRX","LTC","ADA","XRP"]
        # for i in coins:
        #     get_binance_order_book(i)

    return render_template('index.html',coin_id=coin_id,coins=coins)

@app.route('/coin/<coin_id>')
def order_book(coin_id):
    data = get_binance_order_book(coin_id.upper())
    bids = []
    asks = []

    if data:
        bids_data = data.get('bids', [])
        asks_data = data.get('asks', [])
        
        for bid in bids_data:
            price = float(bid[0])
            volume = float(bid[1])
            total = price * volume
            bids.append({
                'volume': round(volume,5),
                'price': price,
                'total': round(total,3)
            })

        for ask in asks_data:
            price = float(ask[0])
            volume = float(ask[1])
            total = price * volume
            asks.append({
                'volume': round(volume,5),
                'price': price,
                'total': round(total,3)
            })
        # return jsonify({'bids': bids, 'asks': asks})
    return render_template('order_book.html', coin_id=coin_id)

@app.route('/coin/<coin_id>/data')
def order_book_data(coin_id):
    data = get_binance_order_book(coin_id.upper())
    bids = []
    asks = []
    if data:
        bids_data = data.get('bids', [])
        asks_data = data.get('asks', [])
        for bid in bids_data:
            price = float(bid[0])
            volume = float(bid[1])
            total = price * volume
            bids.append({'volume': round(volume,5), 'price': price, 'total': round(total,3)})
        for ask in asks_data:
            price = float(ask[0])
            volume = float(ask[1])
            total = price * volume
            asks.append({'volume': round(volume,5), 'price': price, 'total': round(total,3)})

    return jsonify({'bids': bids, 'asks': asks})

if __name__ == '__main__':
    app.run(debug=True)