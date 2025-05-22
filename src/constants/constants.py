AVRO_COINBASE_PRODUCER_TICKER_SCHEMA = {
    "type": "record",
    "name": "Ticker",
    "namespace": "coinbase",
    "fields": [
        {"name": "product_id", "type": ["null", "string"], "default": None},
        {"name": "type", "type": ["null", "string"], "default": None},
        {"name": "price", "type": ["null", "string"], "default": None},
        {"name": "open_24h", "type": ["null", "string"], "default": None},
        {"name": "volume_24h", "type": ["null", "string"], "default": None},
        {"name": "high_24h", "type": ["null", "string"], "default": None},
        {"name": "side", "type": ["null", "string"], "default": None},
        {"name": "time", "type": ["null", "string"], "default": None},
    ],
}
