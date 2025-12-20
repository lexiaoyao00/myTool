from interface import Publisher, Subscriber, PubSubManager
import time

from loguru import logger
import sys

# 示例1: 简单的发布订阅
def simple_example():
    print("\n=== 简单发布订阅示例 ===\n")

    # 创建发布者
    publisher = Publisher("tcp://127.0.0.1:5555")

    # 创建订阅者
    subscriber = Subscriber("tcp://127.0.0.1:5555")

    # 定义回调函数
    def on_message(topic, data):
        print(f"Received - Topic: {topic}, Data: {data}")

    # 订阅主题
    subscriber.subscribe("sensor", on_message)
    subscriber.subscribe("alert", on_message)

    # 开始监听
    subscriber.start_listening()

    # 等待订阅者准备好
    time.sleep(0.5)

    # 发布消息
    for i in range(5):
        publisher.publish("sensor.temperature", {"value": 20 + i, "unit": "°C"})
        publisher.publish("alert.warning", {"message": f"Warning {i}"})
        time.sleep(0.5)

    # 清理
    time.sleep(1)
    subscriber.close()
    publisher.close()


# 示例2: 使用管理器
def manager_example():
    print("\n=== 使用管理器示例 ===\n")

    # 创建管理器
    manager = PubSubManager(
        pub_address="tcp://127.0.0.1:5556",
        sub_addresses=["tcp://127.0.0.1:5556"]
    )

    # 定义回调
    def handle_data(topic, data):
        print(f"Manager received - Topic: {topic}, Data: {data}")

    # 订阅
    manager.subscribe("tcp://127.0.0.1:5556", "data", handle_data)

    time.sleep(0.5)

    # 发布
    for i in range(3):
        manager.publish("data.test", {"count": i})
        time.sleep(0.5)

    time.sleep(1)
    manager.close()


# 示例3: 多个订阅者
def multiple_subscribers_example():
    print("\n=== 多个订阅者示例 ===\n")

    publisher = Publisher("tcp://127.0.0.1:5557")

    # 创建多个订阅者
    subscribers = []
    for i in range(3):
        sub = Subscriber("tcp://127.0.0.1:5557")

        # 每个订阅者有自己的回调
        def make_callback(sub_id):
            def callback(topic, data):
                print(f"Subscriber {sub_id} - Topic: {topic}, Data: {data}")
            return callback

        sub.subscribe("broadcast", make_callback(i))
        sub.start_listening()
        subscribers.append(sub)

    time.sleep(0.5)

    # 发布广播消息
    for i in range(3):
        publisher.publish("broadcast", {"message": f"Broadcast {i}"})
        time.sleep(0.5)

    time.sleep(1)

    # 清理
    for sub in subscribers:
        sub.close()
    publisher.close()


# 使用示例
if __name__ == "__main__":
    logger.remove()
    logger.add(sink='storage/logs/debug.log', encoding='utf-8', level='DEBUG', rotation='10 MB', retention='10 days')
    # 运行示例
    # simple_example()
    # manager_example()
    multiple_subscribers_example()
