from abc import ABC, abstractmethod


class BaseStreamProducer(ABC):

    @abstractmethod
    def on_message(self, *args, **kwargs):
        pass

    @abstractmethod
    def on_error(self, *args, **kwargs):
        pass

    @abstractmethod
    def on_close(self, *args, **kwargs):
        pass

    @abstractmethod
    def on_open(self, *args, **kwargs):
        pass

    @abstractmethod
    def run(self):
        pass
