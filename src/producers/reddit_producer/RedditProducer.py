import praw
import logging
from textblob import TextBlob
from src.interfaces.BaseStreamProducer import BaseStreamProducer
from src.constants.Dataclass import RedditMessage
from src.constants.Enums import ProducerApplicationEnum
from src.generic.KafkaProducer import KafkaProducer
from src.generic.LoggingDecorator import log_method
from typing import List


class RedditProducer(BaseStreamProducer, KafkaProducer):
    """
    RedditProducer streams Reddit comments, analyzes their sentiment, and produces them to Kafka topics.
    """

    def __init__(
        self, topic_suffix: List[str], client_id: str, client_secret: str
    ) -> None:
        """
        Initialize the RedditProducer.

        Args:
            topic_suffix (List[str]): List of subreddit names to subscribe to.
            client_id (str): Reddit API client ID.
            client_secret (str): Reddit API client secret.
        """
        self.message_schema = RedditMessage.avro_schema()

        KafkaProducer.__init__(
            self,
            topic_suffix=topic_suffix,
            application=ProducerApplicationEnum.REDDIT.value,
        )

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="sentimentTracker",
        )
        self.running = False
        self.topic_suffix = topic_suffix

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze the sentiment of a given text using TextBlob.

        Args:
            text (str): The text to analyze.

        Returns:
            str: Sentiment label ('Positive', 'Negative', or 'Neutral').
        """
        analysis = TextBlob(text)
        sentiment = analysis.sentiment.polarity
        sentiment_label = (
            "Positive"
            if sentiment > 0.1
            else "Negative"
            if sentiment < -0.1
            else "Neutral"
        )
        return sentiment_label

    @log_method("RedditProducer.on_message")
    def on_message(self, message) -> None:
        """
        Handle incoming Reddit comment, analyze sentiment, and produce to Kafka.

        Args:
            message: Reddit comment object.
        """
        data = {}
        sentiment_label = self.analyze_sentiment(message.body)
        data["id"] = str(message.id)
        data["topic"] = message.subreddit.display_name
        data["sentiment"] = sentiment_label
        data["user"] = message.author.name
        data["message"] = message.body
        filtered_message = self.filter_message(RedditMessage, data)
        if data["topic"] in self.topics.keys():
            key = filtered_message["id"]
            self.send(
                topic=self.topics[filtered_message["topic"]],
                key=key,
                value=filtered_message,
            )

    def on_error(self, error: Exception) -> None:
        """
        Handle errors during Reddit streaming.

        Args:
            error (Exception): The error encountered.
        """
        logging.error(f"Reddit Error: {error}")

    def on_close(self) -> None:
        """
        Handle Reddit stream closure event.
        """
        logging.info("Reddit stream closed.")

    def on_open(self) -> None:
        """
        Handle Reddit stream open event.
        """
        logging.info("Starting live Reddit stream for Bitcoin-related comments...")

    @log_method("RedditProducer.run")
    def run(self) -> None:
        """
        Start streaming Reddit comments and producing them to Kafka.
        """
        self.on_open()
        self.running = True
        try:
            for comment in self.reddit.subreddit(
                "+".join(self.topic_suffix)
            ).stream.comments(skip_existing=True):
                # if "bitcoin" in comment.body.lower():
                self.on_message(comment)
        except Exception as e:
            self.on_error(e)
        finally:
            self.on_close()
