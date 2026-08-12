import requests
import pandas as pd
import numpy as np
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ১. Delta Demo API Credentials
API_KEY = 'XQjzXkuuUf6vqm0Q4HdVNWf846A4tl'
API_SECRET = '0UcXR6lSdU5iYkrjcZVuNujUAEMnqs1rsft0oiVKYsyWdujQ09BOUrxRUsh2'

# Render Web Service Port Binding Dummy Server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"24/7 Delta Demo Trading Bot is Running!")

def run_dummy_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Render Web Server started on port 10000", flush=True)
    httpd.serve_forever()

# ২. Delta Public History API থেকে ক্যান্ডেল ডেটা ফেচ
def fetch_delta_candles(symbol="BTCUSD", resolution="1"):
    url = "https://api.india.delta.exchange/v2/chart/history"
    end_time = int(time.time())
    start_time = end_time - (100 * 60) # Last 100 minutes
    
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

# ৩. ট্রেডিং লুপ
def main_bot_loop():
    symbol = "BTCUSD"
    print("--- 24/7 Delta Demo Bot Started on Render ---", flush=True)
    last_trade_time = 0

    while True:
        try:
            df = fetch_delta_candles(symbol=symbol, resolution="1")
            if not df.empty:
                current_price = df['Close'].iloc[-1]
                sup = df['Low'].rolling(10).min().iloc[-1]
                res = df['High'].rolling(10).max().iloc[-1]

                current_time = time.time()

                if current_time - last_trade_time > 300: # 5 mins cooldown
                    if current_price <= sup * 1.0005:
                        print(f"[{time.ctime()}] 🚀 BUY Signal Matched at ${current_price}", flush=True)
                        last_trade_time = current_time
                    elif current_price >= res * 0.9995:
                        print(f"[{time.ctime()}] 🚀 SELL Signal Matched at ${current_price}", flush=True)
                        last_trade_time = current_time
                    else:
                        print(f"[{time.ctime()}] Live BTC Price: ${current_price:,.2f} | Watching Market...", flush=True)
            
            time.sleep(20)

        except Exception as e:
            print(f"[{time.ctime()}] Loop Error: {e}", flush=True)
            time.sleep(20)

if __name__ == "__main__":
    # ডামি ওয়েব সার্ভার ব্যাকগ্রাউন্ডে স্টার্ট
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    # মূল ট্রেডিং বট চালু
    main_bot_loop()
