from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from src.constants.constants import AVRO_COINBASE_PRODUCER_TICKER_SCHEMA
from src.interfaces.BaseKafkaProducer import BaseKafkaProducer
from src.interfaces.BaseStreamProducer import BaseStreamProducer

from src.generic.SchemaRegistryClient import SchemaRegistryClient
from confluent_kafka.serialization import (
    SerializationContext,
    MessageField,
)
import os


class KafkaProducer(BaseKafkaProducer, SchemaRegistryClient):
    def __init__(self, producer, symbols, application):
        # Detect if running in Docker
        self.application = application
        in_docker = os.environ.get("IN_DOCKER", "0") == "1"
        if in_docker:
            bootstrap_servers = os.environ.get(
                "KAFKA_BOOTSTRAP_SERVERS", "broker:29092"
            )
        else:
            bootstrap_servers = os.environ.get(
                "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
            )
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = AdminClient({"bootstrap.servers": self.bootstrap_servers})
        self.topics = {}
        SchemaRegistryClient.__init__(self, url="http://localhost:8081")
        self.ensure_topics_exists(producer, symbols)

        self.producer = Producer({"bootstrap.servers": self.bootstrap_servers})

    def send(self, topic: str, key: str, value: dict) -> None:
        self.producer.produce(
            topic,
            key=self.string_serializer(key),
            value=self.avro_serializer(
                value, SerializationContext(topic, MessageField.VALUE)
            ),
        )
        self.producer.flush()

    def ensure_topics_exists(self, producer: BaseStreamProducer, symbols: list) -> None:
        topic_metadata = self.admin_client.list_topics(timeout=5)
        for symbol in symbols:
            topic = f"{producer}_{symbol}"
            if topic not in topic_metadata.topics:
                new_topic = [NewTopic(topic, num_partitions=1, replication_factor=1)]
                self.admin_client.create_topics(new_topic)

            self.topics[symbol] = topic
