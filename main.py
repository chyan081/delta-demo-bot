import requests
import pandas as pd
import numpy as np
import time
import hmac
import hashlib
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ১. Delta Demo API Credentials
API_KEY = 'XQjzXkuuUf6vqm0Q4HdVNWf846A4tl'
API_SECRET = '0UcXR6lSdU5iYkrjcZVuNujUAEMnqs1rsft0oiVKYsyWdujQ09BOUrxRUsh2'
BASE_URL = 'https://demo-api.delta.exchange'

# Render Port Binding Dummy Web Server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"24/7 Delta Demo Live Auto-Trading Bot is Running!")

def run_dummy_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Render Web Server started on port 10000", flush=True)
    httpd.serve_forever()

# ২. API Signature Generator (Order Authentication)
def generate_signature(method, timestamp, path, query_string="", payload=""):
    signature_data = method + timestamp + path + query_string + payload
    message = bytes(signature_data, 'utf-8')
    secret = bytes(API_SECRET, 'utf-8')
    return hmac.new(secret, message, hashlib.sha256).hexdigest()

# ৩. Delta Demo Market Order Execution Function
def place_delta_demo_order(product_id=1, size=1, side="buy"): # Product ID 1 = BTCUSD Perpetual
    endpoint = "/v2/orders"
    url = BASE_URL + endpoint
    timestamp = str(int(time.time()))
    
    payload_dict = {
        "product_id": product_id,
        "size": size,
        "side": side,
        "order_type": "market_order"
    }
    payload = json.dumps(payload_dict)
    
    signature = generate_signature("POST", timestamp, endpoint, payload=payload)
    
    headers = {
        'api-key': API_KEY,
        'timestamp': timestamp,
        'signature': signature,
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        res_data = response.json()
        if response.status_code in [200, 201] and res_data.get('success'):
            order_info = res_data.get('result', {})
            print(f"[{time.ctime()}] 🎉 DEMO TRADE EXECUTED SUCCESSFULLY! Side: {side.upper()} | Order ID: {order_info.get('id')}", flush=True)
            return res_data
        else:
            print(f"[{time.ctime()}] ❌ Execution Error: {res_data}", flush=True)
    except Exception as e:
        print(f"[{time.ctime()}] ❌ Order Request Failed: {e}", flush=True)
    return None

# ৪. Public Candle Data Fetcher
def fetch_delta_candles(symbol="BTCUSD", resolution="1"):
    url = "https://api.india.delta.exchange/v2/chart/history"
    end_time = int(time.time())
    start_time = end_time - (100 * 60)
    
    params = {
        'symbol': symbol,
        'resolution': str(resolution),
        'from': start_time,
        'to': end_time
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        data = res.json()
        if res.status_code == 200 and data.get('success'):
            result = data.get('result', [])
            if not result:
                res_g = requests.get("https://api.delta.exchange/v2/chart/history", params=params, headers=headers, timeout=10)
                result = res_g.json().get('result', [])
            if result:
                df = pd.DataFrame(result)
                df['Datetime'] = pd.to_datetime(df['t'], unit='s')
                df.set_index('Datetime', inplace=True)
                df.sort_index(inplace=True)
                df = df.rename(columns={'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'})
                cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                df[cols] = df[cols].astype(float)
                return df[cols]
    except Exception as e:
        print(f"Error fetching candles: {e}", flush=True)
        
    return pd.DataFrame()

# ৫. Main Trading Loop
def main_bot_loop():
    symbol = "BTCUSD"
    print("--- 24/7 Delta Demo Live Order Bot Started ---", flush=True)
    last_trade_time = 0

    while True:
        try:
            df = fetch_delta_candles(symbol=symbol, resolution="1")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                sup = df['Low'].rolling(10).min().iloc[-1]
                res = df['High'].rolling(10).max().iloc[-1]

                current_time = time.time()

                if current_time - last_trade_time > 300: # 5 Minutes Cooldown
                    if current_price <= sup * 1.0005:
                        print(f"[{time.ctime()}] 🚀 BUY Signal Triggered at ${current_price}", flush=True)
                        place_delta_demo_order(product_id=1, size=1, side="buy")
                        last_trade_time = current_time
                    elif current_price >= res * 0.9995:
                        print(f"[{time.ctime()}] 🚀 SELL Signal Triggered at ${current_price}", flush=True)
                        place_delta_demo_order(product_id=1, size=1, side="sell")
                        last_trade_time = current_time
                    else:
                        print(f"[{time.ctime()}] BTC Price: ${current_price:,.2f} | Watching Strategy...", flush=True)
            
            time.sleep(20)

        except Exception as e:
            print(f"[{time.ctime()}] Loop Error: {e}", flush=True)
            time.sleep(20)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    main_bot_loop()
