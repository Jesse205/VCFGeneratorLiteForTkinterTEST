import threading
import time
from vcf_generator_lite.utils.deque_queue import DequeQueue


class TestDequeQueue:
    """测试 DequeQueue 的基本功能"""

    def test_initialization(self):
        """测试初始化"""
        queue = DequeQueue(max_size=10)
        assert queue.max_size == 10
        assert len(queue.deque) == 0

    def test_put_and_get(self):
        """测试基本的 put 和 get 操作"""
        queue = DequeQueue(max_size=5)

        # 添加元素
        queue.put("item1")
        queue.put("item2")

        # 获取元素
        assert queue.get() == "item1"
        assert queue.get() == "item2"

    def test_max_size_limit(self):
        """测试最大大小限制"""
        queue = DequeQueue(max_size=2)

        queue.put("item1")
        queue.put("item2")
        # 队列已满，put 应该阻塞（但在测试中我们验证队列长度）
        assert len(queue.deque) == 2

    def test_empty_queue_get(self):
        """测试从空队列获取元素（需要在单独线程中测试阻塞行为）"""
        queue = DequeQueue(max_size=5)

        # 在单独线程中测试 get 的阻塞行为
        def get_item():
            return queue.get()

        thread = threading.Thread(target=get_item)
        thread.start()

        # 短暂等待让线程开始阻塞
        time.sleep(0.1)

        # 添加一个元素解除阻塞
        queue.put("test_item")
        thread.join(timeout=1.0)  # 设置超时避免测试挂起

        # 验证队列状态
        assert len(queue.deque) == 0


class TestDequeQueueConcurrency:
    """测试 DequeQueue 的并发安全性"""

    def test_multiple_producers_consumers(self):
        """测试多生产者 - 多消费者场景"""
        queue = DequeQueue(max_size=10)
        results = []
        errors = []

        def producer(items):
            try:
                for item in items:
                    queue.put(item)
            except Exception as e:
                errors.append(e)

        def consumer(consume_count):
            try:
                for _ in range(consume_count):
                    item = queue.get()
                    results.append(item)
            except Exception as e:
                errors.append(e)

        # 创建多个生产者和消费者
        producers = []
        consumers = []

        # 生产者线程
        for i in range(2):
            thread = threading.Thread(target=producer, args=([f"item_{i}_{j}" for j in range(5)],))
            producers.append(thread)

        # 消费者线程
        for i in range(2):
            thread = threading.Thread(target=consumer, args=(5,))
            consumers.append(thread)

        # 启动所有线程
        for thread in producers + consumers:
            thread.start()

        # 等待所有线程完成
        for thread in producers + consumers:
            thread.join(timeout=2.0)  # 设置超时

        # 验证结果
        assert len(errors) == 0, f"并发操作中出现错误：{errors}"
        assert len(results) == 10, f"期望 10 个结果，实际得到{len(results)}"
        assert len(set(results)) == 10, "结果中存在重复项"
