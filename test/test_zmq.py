import sys
import os

# 把 src 目录加到搜索路径的最前面
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from interface import *
import time

# 使用示例
if __name__ == "__main__":
    # 示例1: 发布-订阅模式
    def test_pub_sub():
        print("\n=== Testing Pub-Sub Pattern ===")

        # 创建发布者
        pub = Publisher("tcp://*:5555")

        # 创建订阅者
        sub = Subscriber("tcp://localhost:5555", topics=["weather", "news"])

        # 设置回调函数
        def on_message(topic, data):
            print(f"Received [{topic}]: {data}")

        # 启动异步接收
        sub.start_receiving(on_message)

        # 发布消息
        for i in range(5):
            pub.publish("weather", {"temp": 20 + i, "humidity": 60})
            pub.publish("news", {"headline": f"News {i}"})
            pub.publish("sports", {"score": i})  # 这个不会被接收
            time.sleep(0.5)

        time.sleep(1)

        # 清理
        sub.close()
        pub.close()

    # 示例2: 请求-响应模式
    def test_req_rep():
        print("\n=== Testing Request-Reply Pattern ===")

        # 创建响应者（服务器）
        responder = Responder("tcp://*:5556")

        # 定义处理函数
        def handle_request(data):
            print(f"Server received: {data}")
            if isinstance(data, dict) and "number" in data:
                return {"result": data["number"] * 2}
            return {"error": "Invalid request"}

        # 启动服务器
        responder.start(handle_request)

        # 创建请求者（客户端）
        requester = Requester("tcp://localhost:5556")

        # 发送请求
        for i in range(5):
            response = requester.request({"number": i})
            print(f"Client received: {response}")
            time.sleep(0.5)

        # 清理
        requester.close()
        responder.close()

    # 运行测试
    test_pub_sub()
    test_req_rep()
