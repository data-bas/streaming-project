import logging
from functools import wraps

# Configure root logger if not already configured
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


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
                # If method is on_message, try to extract product_id from message
                if func.__name__ == "on_message" and len(args) > 1:
                    try:
                        import json

                        data = json.loads(args[1])
                        product_id = data.get("product_id")
                        if hasattr(self, "topics") and product_id in self.topics:
                            topic = self.topics[product_id]
                    except Exception:
                        pass
                # For send, topic is usually the first arg
                elif func.__name__ == "send" and hasattr(self, "topics"):
                    if args[0] in self.topics.values():
                        topic = args[0]
            log_msg = f"[app={app}] [topic={topic}] data={data}"
            logging.info(log_msg)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
