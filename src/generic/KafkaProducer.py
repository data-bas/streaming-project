from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from src.interfaces.BaseKafkaProducer import BaseKafkaProducer
from src.interfaces.BaseWebSocketProducer import BaseStreamProducer
import os


class GenericKafkaProducer(BaseKafkaProducer):
    def __init__(self, producer, symbols):
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
        self.producer = Producer({"bootstrap.servers": self.bootstrap_servers})
        self.admin_client = AdminClient({"bootstrap.servers": self.bootstrap_servers})
        self.topics = {}
        self.ensure_topics_exists(
            producer, symbols, num_partitions=1, replication_factor=1
        )

    def send(self, topic: str, key: str, value: dict) -> None:
        self.producer.produce(topic, key=key, value=str(value))
        self.producer.flush()

    def ensure_topics_exists(
        self,
        producer: BaseStreamProducer,
        symbols: list,
        num_partitions: int,
        replication_factor: int,
    ) -> None:
        topic_metadata = self.admin_client.list_topics(timeout=5)
        for symbol in symbols:
            topic = f"{producer}_{symbol}"
            if topic not in topic_metadata.topics:
                new_topic = [NewTopic(topic, num_partitions, replication_factor)]
                self.admin_client.create_topics(new_topic)

            self.topics[symbol] = topic
