import collections
from threading import Condition


class DequeQueue[T]:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.deque = collections.deque(maxlen=max_size)
        self.condition = Condition()

    def put(self, item: T):
        with self.condition:
            while len(self.deque) >= self.max_size:
                self.condition.wait()
            self.deque.append(item)
            self.condition.notify_all()

    def get(self) -> T:
        with self.condition:
            while len(self.deque) == 0:
                self.condition.wait()
            item = self.deque.popleft()
            self.condition.notify_all()
            return item
