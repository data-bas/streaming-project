from abc import ABC, abstractmethod
from src.interfaces.BaseWebSocketProducer import BaseStreamProducer


class BaseKafkaProducer(ABC):
    @abstractmethod
    def send(self, topic: str, key: str, value: dict):
        pass

    @abstractmethod
    def ensure_topics_exists(self, producer: BaseStreamProducer, symbols: list):
        pass
