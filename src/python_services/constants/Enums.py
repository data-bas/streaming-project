from enum import Enum
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer


class ProducerApplicationEnum(Enum):
    """
    Enum for application names.
    """

    COINBASE = "coinbase"
    REDDIT = "reddit"


class SerializerEnum(Enum):
    """
    Enum for serializer types.
    """

    AVRO = AvroSerializer
    STRING = StringSerializer
