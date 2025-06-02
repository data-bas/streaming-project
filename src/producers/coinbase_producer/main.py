import argparse
from dotenv import load_dotenv

from src.producers.coinbase_producer.CoinbaseProducer import CoinbaseProducer


load_dotenv()


def parse_topics() -> argparse.Namespace:
    """Parse a comma-separated string of topics into a list."""
    parser = argparse.ArgumentParser(description="Run Coinbase Producer with topics.")
    parser.add_argument(
        "--topics",
        type=str,
        required=False,
        help="Comma-separated list of topics, e.g. BTC-USD,XRP-USD,ETH-USD",
        default="BTC-USD,XRP-USD,ETH-USD",
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_topics()
    symbols = [topic.strip() for topic in args.topics.split(",") if topic.strip()]
    coin_base_producer = CoinbaseProducer(symbols)
    coin_base_producer.run()
