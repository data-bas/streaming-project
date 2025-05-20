import json
import websocket
from src.interfaces.BaseWebSocketProducer import BaseStreamProducer


class CoinbaseProducer(BaseStreamProducer):
    def __init__(self, symbol=None):
        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.symbol = symbol

    def on_message(self, ws, message):
        data = json.loads(message)
        print(data)

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"Close status code: {close_status_code}, message: {close_msg}")

    def on_open(self, ws):
        subscribe_message = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": self.symbol}]
        }
        ws.send(json.dumps(subscribe_message))
    
    def run(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.run_forever()