from src.constants.Enums import SerializerEnum

class Serializer:
    
    def __init__(self, serializer_type):
        self.serializer_type = serializer_type
        self.serializer = self.get_serializer(serializer_type)
        self.string_serializer = SerializerEnum.STRING.value("utf_8")

    def get_serializer(self, serializer_type):
        if serializer_type == SerializerEnum.AVRO:
            return self.create_avro_serializer()
        else:
            raise ValueError(f"Unsupported serializer type: {serializer_type}")
        
        
    def create_avro_serializer(self):  # Serializer klassen
        schema = (
            AVRO_COINBASE_PRODUCER_TICKER_SCHEMA
            if self.application == "coinbase"
            else None
        )  # TODO: # ENUM implementatie + Dataclass
        schema_str = json.dumps(schema)
        self.avro_serializer = SerializerEnum.AVRO.value(
            self.schema_registry_client,
            schema_str,
            conf={"auto.register.schemas": True},
        )