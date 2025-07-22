import json
import websocket
import logging
from src.python_services.interfaces.BaseStreamProducer import BaseStreamProducer
from src.python_services.generic.KafkaProducer import KafkaProducer
from src.python_services.constants.Enums import ProducerApplicationEnum
from src.python_services.constants.Dataclass import CoinbaseMessage
from src.python_services.generic.LoggingDecorator import log_method
from typing import List


class CoinbaseProducer(BaseStreamProducer, KafkaProducer):
    """
    CoinbaseProducer streams real-time data from Coinbase via WebSocket and produces messages to Kafka topics.
    """

    def __init__(self, topic_suffix: List[str]) -> None:
        """
        Initialize the CoinbaseProducer.

        Args:
            topic_suffix (List[str]): List of product IDs to subscribe to and produce messages for.
        """
        self.message_schema = CoinbaseMessage.avro_schema()  # TODO: Onoverzichtelijk want wordt pas gebruikt in SchemRegistry, anders doorgeven via KafkaProducer.

        KafkaProducer.__init__(
            self,
            topic_suffix=topic_suffix,
            application=ProducerApplicationEnum.COINBASE.value,
        )

        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.topic_suffix = topic_suffix

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """
        Handle incoming WebSocket messages and produce them to Kafka.

        Args:
            ws (websocket.WebSocketApp): The WebSocket connection.
            message (str): The received message as a JSON string.
        """
        data = json.loads(message)
        product_id = data.get("product_id")

        if product_id in self.topics.keys():
            key = str(data.get("trade_id"))
            message = self.filter_message(CoinbaseMessage, data, topic=self.topics[product_id])

            self.send(topic=self.topics[product_id], key=key, value=message)
            
    @log_method("Error occurred in Coinbase stream")
    def on_error(self, ws: websocket.WebSocketApp, error: str) -> None:
        """
        Handle WebSocket errors.

        Args:
            ws (websocket.WebSocketApp): The WebSocket connection.
            error (str): The error message.
        """
        logging.error(f"Error: {error}")  # TODO: Log error appropriately

    @log_method("Connection closed")
    def on_close(
        self, ws: websocket.WebSocketApp, close_status_code: str, close_msg: str
    ) -> None:
        """
        Handle WebSocket closure events.

        Args:
            ws (websocket.WebSocketApp): The WebSocket connection.
            close_status_code (str): The close status code.
            close_msg (str): The close message.
        """
        logging.info(
            f"Close status code: {close_status_code}, message: {close_msg}"
        )  # TODO: Log error appropriately

    @log_method("WebSocket connection opened - subscribing to channels")
    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """
        Handle WebSocket open event and subscribe to product channels.

        Args:
            ws (websocket.WebSocketApp): The WebSocket connection.
        """
        subscribe_message = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": self.topic_suffix}],
        }
        ws.send(json.dumps(subscribe_message))

    @log_method("Starting Coinbase stream")
    def run(self) -> None:
        """
        Start the WebSocket client and begin streaming data from Coinbase.
        """
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()
