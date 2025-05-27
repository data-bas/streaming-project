from dataclasses import dataclass
from dataclasses_avroschema import AvroModel


@dataclass
class CoinbaseMessage(AvroModel):
    product_id: str
    type: str
    price: str
    open_24h: str
    volume_24h: str
    high_24h: str
    side: str
    time: str
