import pytest
import requests

# Flask 서버 URL
BASE_URL = "http://127.0.0.1:5000"

# 샘플 주문 데이터
sample_order = {
    "order_id": "003",
    "customer_id": "C003",
    "customer_name": "Alice Johnson",
    "order_date": "2023-11-11T09:15:00",
    "order_status": "처리 중",
    "campaign_id": "CAM003",
    "items": [
        {"product_id": "P1003", "product_name": "노트북", "quantity": 1}
    ]
}

@pytest.fixture(scope="module")
def collect_order():
    """새로운 주문을 수집하는 테스트"""
    response = requests.post(f"{BASE_URL}/collect_order", json=sample_order)
    assert response.status_code == 200
    assert response.json()["message"] == f"주문{sample_order['order_id']} 가 성공적으로 수집되었습니다."
    return sample_order["order_id"]

def test_get_order(collect_order):
    """특정 주문을 조회하는 테스트"""
    response = requests.get(f"{BASE_URL}/orders/{collect_order}")
    assert response.status_code == 200
    order_data = response.json()
    assert order_data["order_id"] == collect_order
    assert order_data["customer_name"] == sample_order["customer_name"]

def test_update_order(collect_order):
    """주문 상태를 업데이트하는 테스트"""
    updated_data = {"order_id": collect_order, "order_status": "배송 중"}
    response = requests.post(f"{BASE_URL}/update_order", json=updated_data)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["message"] == f"주문 {collect_order} 가 성공적으로 업데이트되었습니다."

def test_list_orders():
    """모든 주문 목록을 조회하는 테스트"""
    response = requests.get(f"{BASE_URL}/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
