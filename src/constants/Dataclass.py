from dataclasses import dataclass


@dataclass
class CoinbaseMessage:
    product_id: str
    type: str
    price: str
    open_24h: str
    volume_24h: str
    high_24h: str
    side: str
    time: str
