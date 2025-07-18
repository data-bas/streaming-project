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

    def on_message(self, message) -> None:
        """
        Handle incoming Reddit comment, analyze sentiment, and produce to Kafka.

        Args:
            message: Reddit comment object.
        """
        sentiment_label = self.analyze_sentiment(message.body)
        
        # Create RedditMessage dataclass instance
        reddit_message = RedditMessage(
            id=str(message.id),
            subreddit=message.subreddit.display_name,
            author=message.author.name if message.author else None,
            body=message.body,
            sentiment=sentiment_label,
            created_utc=message.created_utc,
            score=message.score,
            parent_id=message.parent_id,
            link_id=message.link_id
        )
        
        # Filter the message using the dataclass
        filtered_message = self.filter_message(RedditMessage, reddit_message.__dict__, topic=self.topics.get(reddit_message.subreddit))
        
        if reddit_message.subreddit in self.topics.keys():
            key = filtered_message["id"]
            self.send(
                topic=self.topics[reddit_message.subreddit],
                key=key,
                value=filtered_message,
            )
    @log_method("Error occurred in Reddit stream")
    def on_error(self, error: Exception) -> None:
        """
        Handle errors during Reddit streaming.

        Args:
            error (Exception): The error encountered.
        """
        logging.error(f"Reddit Error: {error}")

    @log_method("Connection closed")
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
    @log_method("Starting Reddit stream")
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
