from confluent_kafka.schema_registry import (
    SchemaRegistryClient as ConfluentSchemaRegistryClient,
)
from confluent_kafka.schema_registry.avro import AvroSchema, AvroSerializer
from confluent_kafka.schema_registry.error import SchemaRegistryError
import json


# https://developer.confluent.io/courses/kafka-python/producer-class-with-schemas-hands-on/


class SchemaRegistryClient:
    def __init__(self, url: str = "http://localhost:8081"):
        self.client = ConfluentSchemaRegistryClient({"url": url})

    def register_schema(self, subject: str, schema_dict: dict) -> int:

        schema_id = self.client.register_schema(subject, schema_dict)
        # schema_id = self.client.register_schema_full_response(subject, schema_dict)
        print(f"✅ Schema registered with ID: {schema_id}")
        return schema_id

    def get_or_register_schema(self, subject: str, schema_dict: dict) -> AvroSchema:
        try:
            version = self.client.get_latest_version(subject)
            print(f"✅ Schema found for subject '{subject}'")
            return AvroSchema(version.schema.schema_str)
        except SchemaRegistryError as e:
            if e.http_status_code == 404:
                print(f"Geen schema gevonden voor subject '{subject}', registreren...")
                self.register_schema(subject, schema_dict)
                return AvroSchema(json.dumps(schema_dict))
            else:
                raise
