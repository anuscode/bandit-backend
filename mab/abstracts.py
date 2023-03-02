import abc

from mab.context import Context


class MAB(abc.ABC):
    @abc.abstractmethod
    def pull(self):
        pass

    @abc.abstractmethod
    def update(self, context: Context):
        pass

    @abc.abstractmethod
    def reset(self):
        pass
