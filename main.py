import ccxt
import pandas as pd
import numpy as np
import time

# Delta Demo API Credentials
API_KEY = 'XQjzXkuuUf6vqm0Q4HdVNWf846A4tl'
API_SECRET = '0UcXR6lSdU5iYkrjcZVuNujUAEMnqs1rsft0oiVKYsyWdujQ09BOUrxRUsh2'

exchange = ccxt.delta({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

exchange.urls['api'] = {
    'public': 'https://demo-api.delta.exchange',
    'private': 'https://demo-api.delta.exchange',
}

def place_demo_order(symbol, side, amount=1):
    try:
        order = exchange.create_order(symbol=symbol, type='market', side=side, amount=amount)
        print(f"[{time.ctime()}] 🚀 Demo Order Executed! Side: {side.upper()} | ID: {order['id']}", flush=True)
        return order
    except Exception as e:
        print(f"[{time.ctime()}] Order Execution Error: {e}", flush=True)
        return None

def main():
    symbol = 'BTC/USD:USD'
    print("--- 24/7 Delta Demo Bot Started on Render ---", flush=True)
    last_trade_time = 0

    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)
            df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            current_price = df['Close'].iloc[-1]

            sup = df['Low'].rolling(10).min().iloc[-1]
            res = df['High'].rolling(10).max().iloc[-1]

            current_time = time.time()

            if current_time - last_trade_time > 300: # 5 mins cooldown
                if current_price <= sup * 1.0005:
                    print(f"[{time.ctime()}] BUY Signal at ${current_price}", flush=True)
                    place_demo_order(symbol, 'buy', amount=1)
                    last_trade_time = current_time
                elif current_price >= res * 0.9995:
                    print(f"[{time.ctime()}] SELL Signal at ${current_price}", flush=True)
                    place_demo_order(symbol, 'sell', amount=1)
                    last_trade_time = current_time

            time.sleep(10)

        except Exception as e:
            print(f"[{time.ctime()}] Loop Error: {e}", flush=True)
            time.sleep(20)

if __name__ == "__main__":
    main()
