from dataclasses import dataclass
from dataclasses_avroschema import AvroModel
from typing import Optional


@dataclass
class LogMessage:
    level: str
    application: Optional[str]
    topic: Optional[str]
    method: Optional[str]
    message: Optional[str]
    data: Optional[str]  # JSON string representation of data


@dataclass
class CoinbaseMessage(AvroModel):
    """Dataclass for incoming Coinbase comment messages"""
    
    product_id: str
    type: str
    price: str
    open_24h: str
    volume_24h: str
    high_24h: str
    side: str
    time: str


@dataclass
class RedditMessage(AvroModel):
    """Dataclass for incoming Reddit comment messages"""

    id: Optional[str] = None
    subreddit: Optional[str] = None
    author: Optional[str] = None
    body: Optional[str] = None
    sentiment: Optional[str] = None
    created_utc: Optional[float] = None
    score: Optional[int] = None
    parent_id: Optional[str] = None
    link_id: Optional[str] = None
