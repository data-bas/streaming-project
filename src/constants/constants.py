AVRO_COINBASE_PRODUCER_TICKER_SCHEMA = {
    "type": "record",
    "name": "Ticker",
    "namespace": "coinbase",
    "fields": [
        {"name": "type", "type": "string"},
        {"name": "price", "type": "string"},
        {"name": "open_24h", "type": "string"},
        {"name": "volume_24h", "type": "string"},
        {"name": "high_24h", "type": "string"},
        {"name": "side", "type": "string"},
        {"name": "time", "type": "string"}
    ]
}