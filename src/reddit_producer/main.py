import os
from dotenv import load_dotenv

from src.reddit_producer.RedditProducer import RedditProducer


load_dotenv()
if __name__ == "__main__":

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    producer = RedditProducer(
        ["Bitcoin", "CryptoCurrency", "CryptoMarkets", "funny", "AskReddit", "gaming"],
        client_id,
        client_secret,
    )
    producer.run()
