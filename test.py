import requests

base_url = "http://localhost:5000"

# Test Case 1: 기존 주문 상태 업데이트
def test_update_existing_order():
    print("Test Case 1: 기존 주문 상태 업데이트")
    order_id = "1001"
    update_data = {
        "order_id": order_id,
        "customer_name": "홍길동",
        "order_date": "2024-11-10",
        "order_status": "배송 중",  # 상태를 변경
        "campaign_id": "CAMP123"
    }

    response = requests.post(f"{base_url}/update_order", json=update_data)
    
    if response.status_code == 200:
        print(f"주문 {order_id} 상태 업데이트 성공:", response.json())
    else:
        print(f"주문 {order_id} 상태 업데이트 실패:", response.status_code, response.text)

# Test Case 2: 없는 주문 상태 업데이트 (새로운 주문 추가)
def test_update_nonexistent_order():
    print("Test Case 2: 없는 주문 상태 업데이트 (새로운 주문 추가)")
    order_id = "9999"  # 존재하지 않는 주문 ID
    update_data = {
        "order_id": order_id,
        "customer_name": "이몽룡",
        "order_date": "2024-11-10",
        "order_status": "처리 중",
        "campaign_id": "CAMP999"
    }

    response = requests.post(f"{base_url}/update_order", json=update_data)
    
    if response.status_code == 200:
        print(f"주문 {order_id} 상태 업데이트 성공 (새로운 주문 추가됨):", response.json())
    else:
        print(f"주문 {order_id} 상태 업데이트 실패:", response.status_code, response.text)

# Run the test cases
if __name__ == "__main__":
    test_update_existing_order()
    test_update_nonexistent_order()
