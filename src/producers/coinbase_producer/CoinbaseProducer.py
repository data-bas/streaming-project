import json
import websocket
import logging
from src.interfaces.BaseStreamProducer import BaseStreamProducer
from src.generic.KafkaProducer import KafkaProducer
from src.constants.Enums import ProducerApplicationEnum
from src.constants.Dataclass import CoinbaseMessage
from src.generic.LoggingDecorator import log_method


class CoinbaseProducer(BaseStreamProducer, KafkaProducer):
    def __init__(self, symbols):
        self.message_schema = (
            CoinbaseMessage.avro_schema()
        )  # TODO: Onoverzichtelijk want wordt pas gebruikt in SchemRegistry, anders doorgeven via KafkaProducer.

        KafkaProducer.__init__(
            self,
            producer=self,
            symbols=symbols,
            application=ProducerApplicationEnum.COINBASE.value,
        )

        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.symbols = symbols

    def filter_message(self, data: str) -> dict[str, str]:
        fields = CoinbaseMessage.__dataclass_fields__.keys()
        filtered_data = {k: data.get(k) for k in fields}
        message = CoinbaseMessage(**filtered_data)
        return message.__dict__

    @log_method("CoinbaseProducer.on_message")
    def on_message(self, ws, message: str) -> None:
        data = json.loads(message)
        product_id = data.get("product_id")

        if product_id in self.topics.keys():
            key = str(data.get("trade_id"))
            message = self.filter_message(data)

            self.send(topic=self.topics[product_id], key=key, value=message)

    def on_error(self, ws, error: str) -> None:
        logging.error(f"Error: {error}")  # TODO: Log error appropriately

    def on_close(self, ws, close_status_code: str, close_msg: str) -> None:
        logging.info(
            f"Close status code: {close_status_code}, message: {close_msg}"
        )  # TODO: Log error appropriately

    @log_method("CoinbaseProducer.on_open")
    def on_open(self, ws):
        subscribe_message = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": self.symbols}],
        }
        ws.send(json.dumps(subscribe_message))

    @log_method("CoinbaseProducer.run")
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
