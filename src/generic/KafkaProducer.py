from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from src.interfaces.BaseStreamProducer import BaseStreamProducer
from src.constants.Enums import ProducerApplicationEnum

from src.generic.SchemaRegistryClient import SchemaRegistryClient
from confluent_kafka.serialization import (
    SerializationContext,
    MessageField,
)
import os


class KafkaProducer(SchemaRegistryClient):
    def __init__(
        self,
        producer: BaseStreamProducer,
        symbols: list,
        application: ProducerApplicationEnum,
    ):
        self.application = application

        self.check_current_environment()

        self.admin_client = AdminClient({"bootstrap.servers": self.bootstrap_servers})

        SchemaRegistryClient.__init__(self, url=self.schema_registry_url)

        self.topics = {}
        self.ensure_topics_exists(producer, symbols)

        self.producer = Producer({"bootstrap.servers": self.bootstrap_servers})

    def check_current_environment(self):
        in_docker = os.environ.get("IN_DOCKER", "0") == "1"
        if in_docker:
            self.bootstrap_servers = "broker1:29092,broker2:29094"
            self.schema_registry_url = "http://schema-registry:8081"
        else:
            self.bootstrap_servers = "localhost:9092"
            self.schema_registry_url = "http://localhost:8081"

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
                new_topic = [NewTopic(topic, num_partitions=4, replication_factor=1)]
                self.admin_client.create_topics(new_topic)

            self.topics[symbol] = topic
