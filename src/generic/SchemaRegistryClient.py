from confluent_kafka.schema_registry import (
    SchemaRegistryClient as ConfluentSchemaRegistryClient,
)
from src.constants.Enums import SerializerEnum
from src.constants.Dataclass import CoinbaseMessage
import json


# https://developer.confluent.io/courses/kafka-python/producer-class-with-schemas-hands-on/


class SchemaRegistryClient:
    def __init__(self, url):
        self.schema_registry_client = ConfluentSchemaRegistryClient({"url": url})
        self.string_serializer = SerializerEnum.STRING.value("utf_8")
        self.create_avro_serializer()  # Dataclass implementatie

    def create_avro_serializer(self):  # Serializer klassen

        schema_str = CoinbaseMessage.avro_schema()
        self.avro_serializer = SerializerEnum.AVRO.value(
            self.schema_registry_client,
            schema_str,
            conf={"auto.register.schemas": True},
        )
