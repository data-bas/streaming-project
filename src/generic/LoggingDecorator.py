import logging
from functools import wraps

# Configure root logger if not already configured
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _extract_on_message_info(producer_instance, args, app):
    """
    Extract topic and data information from on_message method arguments.
    Handles different producer types (Coinbase, Reddit, etc.) dynamically.
    """
    topic = None
    data = None

    try:
        if app == "coinbase":
            # Coinbase: args = (ws, message_json_string)
            if len(args) >= 2:
                import json

                data = json.loads(args[1])
                product_id = data.get("product_id")
                if (
                    hasattr(producer_instance, "topics")
                    and product_id in producer_instance.topics
                ):
                    topic = producer_instance.topics[product_id]

        elif app == "reddit":
            # Reddit: args = (praw_comment_object,)
            if len(args) >= 1:
                message = args[0]
                # Extract subreddit name from PRAW comment object
                if hasattr(message, "subreddit") and hasattr(
                    message.subreddit, "display_name"
                ):
                    subreddit_name = message.subreddit.display_name
                    if (
                        hasattr(producer_instance, "topics")
                        and subreddit_name in producer_instance.topics
                    ):
                        topic = producer_instance.topics[subreddit_name]
                    # Create a summary of the data for logging
                    data = {
                        "id": getattr(message, "id", None),
                        "subreddit": subreddit_name,
                        "author": getattr(message.author, "name", None)
                        if hasattr(message, "author") and message.author
                        else None,
                        "body_preview": getattr(message, "body", "")[:100] + "..."
                        if hasattr(message, "body")
                        and len(getattr(message, "body", "")) > 100
                        else getattr(message, "body", ""),
                    }

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

            log_msg = f"[app={app}] [topic={topic}] data={data}"
            logging.info(log_msg)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
