from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

orders = {}

# 주문 상태 변경을 받는 웹훅 엔드포인트
@app.route('/update_order', methods=['POST'])
def update_order():
    order_data = request.json
    order_id = order_data.get("order_id")
    
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    # 주문이 존재하지 않는 경우 새로운 주문으로 추가
    if order_id not in orders:
        orders[order_id] = order_data
    else:
        # 기존 주문의 상태 업데이트
        orders[order_id].update(order_data)
    
    return jsonify({"message": f"Order {order_id} updated successfully"}), 200


# 외부 주문 시스템에서 실시간으로 데이터를 전달받아 저장하는 엔드포인트
@app.route('/collect_order', methods=['POST'])
def collect_order():
    order_data = request.json
    
    order_id = order_data.get('order_id')
    if not order_id:
        return jsonify({'error': 'Order ID is required'}), 400
    
    # 주문을 인메모리에 저장(주문관리시스템)
    orders[order_id] = order_data
    return jsonify({'message': f'Order {order_id} collected successfully'}), 201

# 주문 조회 엔드포인트 (단일 주문)
@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(order)

# 전체 주문 조회 엔드포인트
@app.route('/orders', methods=['GET'])
def list_orders():
    return jsonify(list(orders.values()))



##외부 시스템으로 주문데이터 전송

EXTERNAL_SYSTEM_URL = "http://external-system-url/api/update_order"

def send_to_external_system(order_data):
    """외부 시스템으로 주문 데이터를 전송하는 함수"""
    try:
        response = requests.post(EXTERNAL_SYSTEM_URL, json=order_data)
        response.raise_for_status()
        print(f"Successfully sent order {order_data['order_id']} to external system.")
    except requests.RequestException as e:
        print(f"Failed to send order {order_data['order_id']} to external system: {e}")

# 주문 상태 변경을 받는 웹훅 엔드포인트
@app.route('/update_order', methods=['POST'])
def update_order():
    order_data = request.json
    order_id = order_data.get("order_id")
    
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    # 주문이 존재하지 않는 경우 새로운 주문으로 추가
    if order_id not in orders:
        orders[order_id] = order_data
    else:
        # 기존 주문의 상태 업데이트
        orders[order_id].update(order_data)
    
    # 상태 변경된 주문 데이터를 외부 시스템에 전송
    send_to_external_system(order_data)
    
    return jsonify({"message": f"Order {order_id} updated successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


---
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# In-memory storage for orders
orders = {}

# 외부 시스템의 URL 설정
TMS_URL = "http://tms-system-url/api/notify_order_status"
TAS_ON_URL = "http://tason-system-url/api/campaign_order"

def send_to_tms(order_data):
    """TMS에 주문 상태 변경을 알림"""
    try:
        response = requests.post(TMS_URL, json=order_data)
        response.raise_for_status()
        print(f"Successfully sent order {order_data['order_id']} status to TMS.")
    except requests.RequestException as e:
        print(f"Failed to send order {order_data['order_id']} status to TMS: {e}")

def send_to_tas_on(order_data):
    """TasOn에 캠페인 관련 주문 데이터 전송"""
    try:
        response = requests.post(TAS_ON_URL, json=order_data)
        response.raise_for_status()
        print(f"Successfully sent order {order_data['order_id']} to TasOn.")
    except requests.RequestException as e:
        print(f"Failed to send order {order_data['order_id']} to TasOn: {e}")

# 주문 수집 엔드포인트
@app.route('/collect_order', methods=['POST'])
def collect_order():
    order_data = request.json
    order_id = order_data.get("order_id")
    campaign_id = order_data.get("campaign_id")  # 캠페인 주문인지 확인

    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400
    
    # 주문을 인메모리에 저장
    orders[order_id] = order_data

    # 캠페인 주문일 경우 TasOn에 전송
    if campaign_id:
        send_to_tas_on(order_data)
    
    return jsonify({"message": f"Order {order_id} collected successfully"}), 201

# 주문 상태 변경 엔드포인트 (웹훅 방식)
@app.route('/update_order', methods=['POST'])
def update_order():
    order_data = request.json
    order_id = order_data.get("order_id")
    
    if not order_id:
        return jsonify({"error": "Order ID is required"}), 400

    # 주문이 존재하지 않는 경우 새로운 주문으로 추가
    if order_id not in orders:
        orders[order_id] = order_data
    else:
        # 기존 주문의 상태 업데이트
        orders[order_id].update(order_data)
    
    # 상태 변경된 주문 데이터를 TMS에 전송
    send_to_tms(order_data)
    
    return jsonify({"message": f"Order {order_id} updated successfully"}), 200

# 단일 주문 조회 엔드포인트
@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)

# 전체 주문 조회 엔드포인트
@app.route('/orders', methods=['GET'])
def list_orders():
    return jsonify(list(orders.values()))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
