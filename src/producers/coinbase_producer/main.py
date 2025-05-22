import os
from dotenv import load_dotenv

from src.producers.coinbase_producer.CoinbaseProducer import CoinbaseProducer


load_dotenv()

if __name__ == "__main__":
    symbols = [topic for topic in os.environ.get("TOPICS").split(",")]
    coin_base_producer = CoinbaseProducer(symbols)
    coin_base_producer.run()
