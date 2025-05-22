from confluent_kafka.schema_registry import (
    SchemaRegistryClient as ConfluentSchemaRegistryClient,
)
from src.constants.constants import AVRO_COINBASE_PRODUCER_TICKER_SCHEMA
from confluent_kafka.schema_registry.avro import AvroSerializer
import json
from confluent_kafka.serialization import StringSerializer

# https://developer.confluent.io/courses/kafka-python/producer-class-with-schemas-hands-on/


class SchemaRegistryClient:
    def __init__(self, url: str = "http://localhost:8081"):
        self.schema_registry_client = ConfluentSchemaRegistryClient({"url": url})
        self.string_serializer = StringSerializer("utf_8")
        self.create_avro_serializer()

    def create_avro_serializer(self):
        schema = AVRO_COINBASE_PRODUCER_TICKER_SCHEMA if self.application == "coinbase" else None # TODO: better approach for this
        schema_str = json.dumps(schema)
        self.avro_serializer = AvroSerializer(
            self.schema_registry_client,
            schema_str,
            conf={"auto.register.schemas": True},
        )
