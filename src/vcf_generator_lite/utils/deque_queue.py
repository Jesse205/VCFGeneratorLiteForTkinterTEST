import collections
from threading import Condition


class ShutDownError(Exception):
    """和 queue 的 Shutdown 一样，不过兼容 Python 3.12 及以前的版本"""


class DequeQueue[T]:
    """一个高性能的队列实现"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.deque = collections.deque(maxlen=max_size)
        self.condition = Condition()
        self.__shutdown = False

    def put(self, item: T):
        with self.condition:
            if self.__shutdown:
                raise ShutDownError
            while len(self.deque) >= self.max_size:
                self.condition.wait()
                if self.__shutdown:
                    raise ShutDownError
            self.deque.append(item)
            self.condition.notify_all()

    def get(self) -> T:
        with self.condition:
            if self.__shutdown:
                raise ShutDownError
            while len(self.deque) == 0:
                self.condition.wait()
                if self.__shutdown:
                    raise ShutDownError
            item = self.deque.popleft()
            self.condition.notify_all()
        return item

    def shutdown(self):
        with self.condition:
            self.__shutdown = True
            self.condition.notify_all()
