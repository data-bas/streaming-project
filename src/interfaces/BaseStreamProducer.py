from abc import ABC, abstractmethod
from src.generic.LoggingDecorator import log_method

class BaseStreamProducer(ABC):

    @abstractmethod
    @log_method("BaseStreamProducer.filter_message")
    def on_message(self, *args, **kwargs):
        pass

    @abstractmethod
    def on_error(self, *args, **kwargs):
        pass

    @abstractmethod
    def on_close(self, *args, **kwargs):
        pass

    @abstractmethod
    @log_method("BaseStreamProducer.on_open")
    def on_open(self, *args, **kwargs):
        pass

    @abstractmethod
    @log_method("BaseStreamProducer.run")
    def run(self):
        pass
