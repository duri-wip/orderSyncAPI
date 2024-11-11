import requests
import json

# 주문 관리 시스템의 API URL
url = "http://localhost:5000/collect_order"

# sample_orders.json 파일 로드
with open('sample_orders.json', 'r', encoding='utf-8') as f:
    orders = json.load(f)

# 각 주문 데이터를 순차적으로 전송
for order_id, order_data in orders.items():
    response = requests.post(url, json=order_data)
    
    if response.status_code == 201:
        print(f"Order {order_id} sent successfully.")
    else:
        print(f"Failed to send order {order_id}: {response.json()}")
