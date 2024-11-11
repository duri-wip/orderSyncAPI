import requests

#외부 시스템 인터페이스 정의
class ExternalSystemInterface:
    def send_orders(self, order_data):
        raise NotImplementedError
    
class TMSInterface(ExternalSystemInterface):
    # TMS_url = 'http://tms-system-url/api/update-order-status'
    TMS_url = 'http://httpbin.org/post'

    def send_order(self, order_data):
        try:
            response = requests.post(self.TMS_url, json=order_data)
            response.raise_for_status()

            print(f"TMS: 주문 {order_data['order_id']}의 상태가 반영되었습니다.")
        except requests.RequestException as e:
            print(f"TMS: 주문 {order_data['order_id']}의 상태 전송 실패 : {e}")

class TasOnInterface(ExternalSystemInterface):
    # TASON_url = 'http://tason-system-url/api/campainge-order'
    TASON_url = 'http://httpbin.org/post'

    def send_order(self, order_data):
        try:
            response = requests.post(self.TASON_url, json=order_data)
            response.raise_for_status()
            
            print(f"TasOn: 주문 {order_data['order_id']}의 상태가 반영되었습니다.")
        except requests.RequestException as e:
            print(f'주문 {order_data["order_id"]}의 상태 전송 실패 : {e}')