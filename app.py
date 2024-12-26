from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import pandas as pd
import requests

app = Flask(__name__)
app.secret_key = 'Chase#7504'

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
    coins = None
    watchlist_coin = session.get('watchlist_coin')
    remove_coin = session.get('remove_coin')
    file_path = r'E:\crypto order book\multiple order book\coins.csv'
    if remove_coin:
        df = pd.read_csv(file_path)
        df = df[df["coins"] != remove_coin]
        df.to_csv(file_path,index=False)
        session.pop('remove_coin', None)
        return jsonify({'status':'success'})

    # appending coin to coins list - watchlist
    df = pd.DataFrame({'coins': [watchlist_coin]})
    if watchlist_coin:
        df.to_csv(file_path, mode='a', header=False, index=False)
        print(f"'{watchlist_coin}' appended to coins.csv")
        session.pop('watchlist_coin',None)

    coins = pd.read_csv(file_path)['coins'].values.flatten().tolist()
    # coins = coins.values.flatten().tolist()
    if request.method == 'POST':
        coin_id = request.form.get('coin_id')
        coin_id = coin_id.upper()
        if coin_id:
            return redirect(url_for('order_book',coin_id=coin_id))

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

@app.route('/coin/<coin_id>/delete')
def delete_coin(coin_id):
    session['remove_coin'] = coin_id.upper()
    return redirect(url_for('home'))

@app.route('/watchlist/<coin_id>')
def watchlist(coin_id):
    session['watchlist_coin'] = coin_id.upper()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)