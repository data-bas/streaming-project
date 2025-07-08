from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from src.constants.Enums import ProducerApplicationEnum

from src.generic.SchemaRegistryClient import SchemaRegistryClient
from src.generic.LoggingDecorator import log_filtered_message
from confluent_kafka.serialization import (
    SerializationContext,
    MessageField,
)
import os
from typing import Dict, List, Any, Type
from dataclasses import dataclass


class KafkaProducer(SchemaRegistryClient):
    """
    KafkaProducer is a generic Kafka producer with schema registry support.
    It manages topic creation, serialization, and message production.
    """

    def __init__(
        self,
        topic_suffix: List[str],
        application: ProducerApplicationEnum,
    ):
        """
        Initialize the KafkaProducer.

        Args:
            topic_suffix (List[str]): List of topic suffixes to create/ensure.
            application (ProducerApplicationEnum): Application enum for topic prefix.
        """
        self.application = application

        self.check_current_environment()

        self.admin_client = AdminClient({"bootstrap.servers": self.bootstrap_servers})

        SchemaRegistryClient.__init__(self, url=self.schema_registry_url)

        self.topics = {}
        self.ensure_topics_exists(topic_suffix)

        self.producer = Producer({"bootstrap.servers": self.bootstrap_servers})

    def check_current_environment(self) -> None:
        """
        Set bootstrap servers and schema registry URL based on environment (Docker or local).
        """
        in_docker = os.environ.get("IN_DOCKER", "0") == "1"
        if in_docker:
            self.bootstrap_servers = "broker1:29092,broker2:29094"
            self.schema_registry_url = "http://schema-registry:8081"
        else:
            self.bootstrap_servers = "localhost:9092,localhost:9093"
            self.schema_registry_url = "http://localhost:8081"

    def send(self, topic: str, key: str, value: Dict[str, Any]) -> None:
        """
        Send a message to a Kafka topic.

        Args:
            topic (str): The topic to send the message to.
            key (str): The message key.
            value (Dict[str, Any]): The message value as a dictionary.
        """
        self.producer.produce(
            topic,
            key=self.string_serializer(key),
            value=self.avro_serializer(
                value, SerializationContext(topic, MessageField.VALUE)
            ),
        )
        self.producer.flush()

    def ensure_topics_exists(self, topic_suffix: List[str]) -> None:
        """
        Ensure that all required topics exist in the Kafka cluster.

        Args:
            topic_suffix (List[str]): List of topic suffixes to create/ensure.
        """
        topic_metadata = self.admin_client.list_topics(timeout=5)
        topic_prefix = self.application
        for suffix in topic_suffix:
            topic = f"{topic_prefix}_{suffix}"
            if topic not in topic_metadata.topics:
                new_topic = [
                    NewTopic(topic, num_partitions=1, replication_factor=1)
                ]  # TODO: topic configuration should be configurable, see remarks.txt
                self.admin_client.create_topics(new_topic)

            self.topics[suffix] = topic

    @log_filtered_message()
    def filter_message(
        self, dataclass_schema: Type[dataclass], data: Dict[str, Any], topic: str = None
    ) -> Dict[str, Any]:
        """
        Filter a dictionary to match the fields of a dataclass schema.

        Args:
            dataclass_schema (Type[dataclass]): The dataclass type to filter against.
            data (Dict[str, Any]): The input data dictionary.
            topic (str): The topic name for logging purposes.

        Returns:
            Dict[str, Any]: Filtered dictionary matching the dataclass fields.
        """
        fields = dataclass_schema.__dataclass_fields__.keys()
        filtered_data = {k: data.get(k) for k in fields}
        message = dataclass_schema(**filtered_data)
        return message.__dict__
