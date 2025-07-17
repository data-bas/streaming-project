from confluent_kafka.schema_registry import (
    SchemaRegistryClient as ConfluentSchemaRegistryClient,
)
from src.python_services.constants.Enums import SerializerEnum


class SchemaRegistryClient:
    """
    SchemaRegistryClient wraps the Confluent Schema Registry client and provides serializers for Kafka messages.
    """

    def __init__(self, url: str):
        """
        Initialize the SchemaRegistryClient.

        Args:
            url (str): The URL of the schema registry service.
        """
        self.schema_registry_client = ConfluentSchemaRegistryClient({"url": url})
        self.string_serializer = SerializerEnum.STRING.value("utf_8")

        self.create_avro_serializer()

    def create_avro_serializer(self) -> None:
        """
        Create an Avro serializer using the schema registry client and message schema.
        """
        self.avro_serializer = SerializerEnum.AVRO.value(
            self.schema_registry_client,
            self.message_schema,
            conf={"auto.register.schemas": True},
        )
