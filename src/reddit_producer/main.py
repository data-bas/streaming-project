from src.reddit_producer.reddit_producer import RedditProducer

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    producer = RedditProducer(["Bitcoin", "CryptoCurrency", "CryptoMarkets", "funny", "AskReddit", "gaming"], client_id, client_secret)
    producer.run()
