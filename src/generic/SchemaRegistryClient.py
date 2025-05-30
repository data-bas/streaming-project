from confluent_kafka.schema_registry import (
    SchemaRegistryClient as ConfluentSchemaRegistryClient,
)
from src.constants.Enums import SerializerEnum


# https://developer.confluent.io/courses/kafka-python/producer-class-with-schemas-hands-on/


class SchemaRegistryClient:
    def __init__(self, url: str):
        self.schema_registry_client = ConfluentSchemaRegistryClient({"url": url})
        self.string_serializer = SerializerEnum.STRING.value("utf_8")
        
        self.create_avro_serializer()

    def create_avro_serializer(self):  # TODO: Serializer klassen
        self.avro_serializer = SerializerEnum.AVRO.value(
            self.schema_registry_client,
            self.message_schema,
            conf={"auto.register.schemas": True},
        )
