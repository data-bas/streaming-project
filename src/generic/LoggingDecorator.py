import logging
import json
from src.constants.Enums import ProducerApplicationEnum
from src.constants.Dataclass import LogMessage, CoinbaseMessage, RedditMessage
from functools import wraps

# Configure root logger if not already configured
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _parse_coinbase_message(message_json_string: str) -> CoinbaseMessage:
    """Parse Coinbase JSON string into CoinbaseInputMessage dataclass"""
    try:
        data = json.loads(message_json_string)
        return CoinbaseMessage(
            product_id=data.get("product_id", ""),
            type=data.get("type", ""),
            price=data.get("price", ""),
            open_24h=data.get("open_24h", ""),
            volume_24h=data.get("volume_24h", ""),
            high_24h=data.get("high_24h", ""),
            side=data.get("side", ""),
            time=data.get("time", "")
        )
    except (json.JSONDecodeError, Exception):
        return CoinbaseMessage(
            product_id="",
            type="",
            price="",
            open_24h="",
            volume_24h="",
            high_24h="",
            side="",
            time=""
        )


def _parse_reddit_message(praw_comment) -> RedditMessage:
    """Parse PRAW comment object into RedditInputMessage dataclass"""
    try:
        return RedditMessage(
            id=getattr(praw_comment, "id", None),
            subreddit=getattr(praw_comment.subreddit, "display_name", None) 
                if hasattr(praw_comment, "subreddit") else None,
            author=getattr(praw_comment.author, "name", None) 
                if hasattr(praw_comment, "author") and praw_comment.author else None,
            body=getattr(praw_comment, "body", None),
            created_utc=getattr(praw_comment, "created_utc", None),
            score=getattr(praw_comment, "score", None),
            parent_id=getattr(praw_comment, "parent_id", None),
            link_id=getattr(praw_comment, "link_id", None)
        )
    except Exception:
        return RedditMessage()


def _extract_on_message_info(producer_instance, args, app):
    """
    Extract topic and data information from on_message method arguments.
    Handles different producer types (Coinbase, Reddit, etc.) dynamically.
    """
    topic = None
    data = None

    try:
        if app == ProducerApplicationEnum.COINBASE.value:
            # Coinbase: args = (ws, message_json_string)
            if len(args) >= 2:
                # Parse into structured dataclass
                coinbase_msg = _parse_coinbase_message(args[1])
                data = coinbase_msg
                
                if (
                    hasattr(producer_instance, "topics")
                    and coinbase_msg.product_id in producer_instance.topics
                ):
                    topic = producer_instance.topics[coinbase_msg.product_id]

        elif app == ProducerApplicationEnum.REDDIT.value:
            # Reddit: args = (praw_comment_object,)
            if len(args) >= 1:
                # Parse into structured dataclass
                reddit_msg = _parse_reddit_message(args[0])
                data = reddit_msg
                
                if (
                    hasattr(producer_instance, "topics")
                    and reddit_msg.subreddit in producer_instance.topics
                ):
                    topic = producer_instance.topics[reddit_msg.subreddit]

        # For other producer types, you can add additional elif blocks here
        else:
            # Generic fallback - try to extract basic info
            if len(args) >= 1:
                message = args[0]
                if hasattr(message, "get"):  # Dict-like object
                    data = dict(message)
                elif hasattr(message, "__dict__"):  # Object with attributes
                    data = {
                        k: v for k, v in vars(message).items() if not k.startswith("_")
                    }

    except Exception:
        # If anything fails, just continue with None values
        pass

    return topic, data


def log_method(message=None):
    """
    Decorator to log entry of important methods, including application and topic if available.
    Dynamically tries to extract topic from arguments or self.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            app = getattr(self, "application", None)
            # Try to extract topic from args or kwargs
            topic = None
            data = None

            # Check for 'topic' in kwargs
            if "topic" in kwargs:
                topic = kwargs["topic"]
            # If not, check if first arg is a topic or product_id
            elif args:
                # If method is on_message, try to extract topic/product_id from message
                if func.__name__ == "on_message":
                    topic, data = _extract_on_message_info(self, args, app)
                # For send, topic is usually the first arg
                elif func.__name__ == "send" and hasattr(self, "topics"):
                    if args[0] in self.topics.values():
                        topic = args[0]

            # Create structured log message
            log_message = LogMessage(
                level="INFO",
                application=app,
                topic=topic,
                method=func.__name__,
                message=message,
                data=json.dumps(data.__dict__) if hasattr(data, '__dict__') else json.dumps(data) if data else None
            )
            
            # Log the structured message
            log_msg = f"[app={log_message.application}] [topic={log_message.topic}] [method={log_message.method}] data={log_message.data}"
            logging.info(log_msg)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
