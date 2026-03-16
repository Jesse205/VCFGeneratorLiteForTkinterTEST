import collections
from queue import ShutDown
from threading import Condition


class DequeQueue[T]:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.deque = collections.deque(maxlen=max_size)
        self.condition = Condition()
        self.__shutdown = False

    def put(self, item: T):
        with self.condition:
            if self.__shutdown:
                raise ShutDown
            while len(self.deque) >= self.max_size:
                self.condition.wait()
                if self.__shutdown:
                    raise ShutDown()
            self.deque.append(item)
            self.condition.notify_all()

    def get(self) -> T:
        with self.condition:
            if self.__shutdown:
                raise ShutDown()
            while len(self.deque) == 0:
                self.condition.wait()
                if self.__shutdown:
                    raise ShutDown()
            item = self.deque.popleft()
            self.condition.notify_all()
        return item

    def shutdown(self):
        with self.condition:
            self.__shutdown = True
            self.condition.notify_all()
