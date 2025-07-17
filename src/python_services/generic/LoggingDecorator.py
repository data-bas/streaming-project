import logging
import json
from src.python_services.constants.Dataclass import LogMessage
from functools import wraps

# Configure root logger if not already configured
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def log_method(message=None):
    """
    log method decorator for generic methods.
    For data-specific logging, use log_filtered_message instead.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            app = getattr(self, "application", None)
            
            # Simple topic extraction for send method only
            topic = None
            if func.__name__ == "send" and hasattr(self, "topics") and args:
                if args[0] in self.topics.values():
                    topic = args[0]
            elif "topic" in kwargs:
                topic = kwargs["topic"]

            # Create structured log message
            log_message = LogMessage(
                level="INFO",
                application=app,
                topic=topic,
                method=func.__name__,
                message=message,
                data=None  # No data logging for generic methods
            )
            
            # Log the structured message
            log_msg = f"[app={log_message.application}] [topic={log_message.topic}] [method={log_message.method}] [message={log_message.message}]"
            logging.info(log_msg)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def log_filtered_message(topic=None):
    """
    Decorator to log the filtered message after the filter_message function is called.
    This logs the structured message data that will be sent to Kafka.
    
    Args:
        topic (str): The topic name to log. If None, will be extracted from kwargs.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Call the original filter_message function
            result = func(self, *args, **kwargs)
            
            # Extract application information
            app = getattr(self, "application", None)
            
            # Use the provided topic parameter or extract from kwargs
            log_topic = topic if topic is not None else kwargs.get("topic", None)
            
            # Create structured log message
            log_message = LogMessage(
                level="INFO",
                application=app,
                topic=log_topic,
                method="on_message",
                message="Filtered message ready for Kafka",
                data=json.dumps(result) if result else None
            )
            
            # Log the structured message
            log_msg = f"[app={log_message.application}] [topic={log_message.topic}] [method={log_message.method}] [message={log_message.message}] data={log_message.data}"
            logging.info(log_msg)
            
            return result
        
        return wrapper
    
    return decorator
