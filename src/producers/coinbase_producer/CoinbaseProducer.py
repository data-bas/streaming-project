import json
import websocket
from src.interfaces.BaseStreamProducer import BaseStreamProducer
from src.generic.KafkaProducer import KafkaProducer
from src.generic.SchemaRegistryClient import SchemaRegistryClient
from src.constants.constants import AVRO_COINBASE_PRODUCER_TICKER_SCHEMA


class CoinbaseProducer(BaseStreamProducer, KafkaProducer):
    def __init__(self, symbols):
        KafkaProducer.__init__(self, producer=self, symbols=symbols)

        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.symbols = symbols

        # self.schema_client = SchemaRegistryClient("http://localhost:8081")
        # self.avro_schema = self.schema_client.get_or_register_schema(
        #    subject="coinbase_producer_BTC-USD",
        #    schema_dict=AVRO_COINBASE_PRODUCER_TICKER_SCHEMA
        # )

    def filter_message(self, data: str) -> dict[str, str]:

        message = {
            "type": data.get("type"),
            "price": data.get("price"),
            "open_24h": data.get("open_24h"),
            "volume_24h": data.get("volume_24h"),
            "high_24h": data.get("high_24h"),
            "side": data.get("side"),
            "time": data.get("time"),
        }
        return message

    def on_message(self, ws, message: str) -> None:
        data = json.loads(message)
        product_id = data.get("product_id")

        if product_id in self.topics.keys():
            key = str(data.get("trade_id"))
            message = self.filter_message(data)

            print(f"Sending message to topic {self.topics[product_id]}: {message}")
            self.send(topic=self.topics[product_id], key=key, value=message)

    def on_error(self, ws, error: str) -> None:
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code: str, close_msg: str) -> None:
        print(f"Close status code: {close_status_code}, message: {close_msg}")

    def on_open(self, ws):
        subscribe_message = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": self.symbols}],
        }
        ws.send(json.dumps(subscribe_message))

    def run(self) -> None:
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()

    def __str__(self) -> str:
        return "coinbase_producer"
