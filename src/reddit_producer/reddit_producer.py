import praw
from textblob import TextBlob
from src.interfaces.BaseWebSocketProducer import BaseStreamProducer

class RedditProducer(BaseStreamProducer):
    def __init__(self, subreddits, client_id, client_secret):
        super().__init__()
        self.subreddits = subreddits
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent='sentimentTracker'
        )
        self.running = False

    def analyze_sentiment(self, text):
        analysis = TextBlob(text)
        return analysis.sentiment.polarity

    def on_message(self, message):
        sentiment = self.analyze_sentiment(message.body)
        sentiment_label = (
            "🟢 Positive" if sentiment > 0.1 else
            "🔴 Negative" if sentiment < -0.1 else
            "⚪ Neutral"
        )
        print(f"[{sentiment_label}] u/{message.author}: {message.body[:100]}...")

    def on_error(self, error):
        print(f"Reddit Error: {error}")

    def on_close(self):
        print("Reddit stream closed.")

    def on_open(self):
        print("Starting live Reddit stream for Bitcoin-related comments...")

    def run(self):
        self.on_open()
        self.running = True
        try:
            for comment in self.reddit.subreddit("+".join(self.subreddits)).stream.comments(skip_existing=True):
                #if "bitcoin" in comment.body.lower():
                self.on_message(comment)
        except Exception as e:
            self.on_error(e)
        finally:
            self.on_close()