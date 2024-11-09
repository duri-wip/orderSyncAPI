from abc import ABC, abstractmethod
import requests
from flask import Flask, jsonify, request
from typing import Dict, List

app = Flask(__name__)

# 주문 데이터 클래스
class Order:
    def __init__(self, order_id: str, customer_name: str, order_date: str, order_status: str):
        self.order_id = order_id
        self.customer_name = customer_name
        self.order_date = order_date
        self.order_status = order_status

# 주문 관리 클래스
class OrderManager:
    def __init__(self):
        self.orders: Dict[str, Order] = {}

    def add_order(self, order: Order):
        self.orders[order.order_id] = order

    def get_order(self, order_id: str) -> Order:
        return self.orders.get(order_id)

    def list_orders(self) -> List[Order]:
        return list(self.orders.values())

# 외부 시스템과의 데이터 연동을 위한 인터페이스
class OrderInterface(ABC):
    @abstractmethod
    def fetch_orders(self):
        pass

    @abstractmethod
    def send_orders(self):
        pass

# OrderInterface를 구현하여 외부 시스템과 통신
class OrderDataHandler(OrderInterface):
    def __init__(self, manager: OrderManager, api_url: str):
        self.manager = manager
        self.api_url = api_url

    def fetch_orders(self):
        try:
            response = requests.get(f"{self.api_url}/orders")
            response.raise_for_status()
            orders_data = response.json()

            for data in orders_data:
                order = Order(data["order_id"], data["customer_name"], data["order_date"], data["order_status"])
                self.manager.add_order(order)
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
        except ValueError as e:
            print(f"Data format error: {e}")

    def send_orders(self):
        orders = self.manager.list_orders()
        orders_json = [
            {
                "order_id": order.order_id,
                "customer_name": order.customer_name,
                "order_date": order.order_date,
                "order_status": order.order_status,
            } for order in orders
        ]

        try:
            response = requests.post(f"{self.api_url}/orders", json=orders_json)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")

# Flask API를 통한 주문 데이터 관리
order_manager = OrderManager()
order_handler = OrderDataHandler(order_manager, "http://external-system.com/api")

@app.route('/orders', methods=['POST'])
def add_order():
    order_data = request.json
    order_id = order_data.get('order_id')
    if order_id in order_manager.orders:
        return jsonify({"error": "Order ID already exists"}), 400

    order = Order(order_data['order_id'], order_data['customer_name'], order_data['order_date'], order_data['order_status'])
    order_manager.add_order(order)
    return jsonify({"message": "Order added successfully"}), 201

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = order_manager.get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.__dict__)

@app.route('/orders', methods=['GET'])
def list_orders():
    orders = order_manager.list_orders()
    return jsonify([order.__dict__ for order in orders])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

