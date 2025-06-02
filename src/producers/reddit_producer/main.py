import os
from dotenv import load_dotenv
import argparse

from src.producers.reddit_producer.RedditProducer import RedditProducer


load_dotenv()


def parse_subreddits() -> argparse.Namespace:
    """Parse a comma-separated string of subreddits into a list."""
    parser = argparse.ArgumentParser(description="Run Reddit Producer with subreddits.")
    parser.add_argument(
        "--subreddits",
        type=str,
        required=False,
        help="Comma-separated list of subreddits, e.g. Bitcoin,CryptoCurrency,CryptoMarkets,funny,AskReddit,gaming",
        default="Bitcoin,CryptoCurrency,CryptoMarkets,funny,AskReddit,gaming",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_subreddits()
    subreddit_list = [sub.strip() for sub in args.subreddits.split(",") if sub.strip()]
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    producer = RedditProducer(
        subreddit_list,
        client_id,
        client_secret,
    )
    producer.run()
