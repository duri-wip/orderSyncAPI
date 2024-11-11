import json
from datetime import datetime
from src.Order import Order  # Order 클래스 임포트 필요

class OrderService:
    def __init__(self):
        self.orders = {}
        self._load_sample_orders()

    def _load_sample_orders(self):
        try:
            with open('/home/sw/orderSyncAPI/data/sample_orders.json', 'r', encoding='utf-8') as f:
                sample_orders = json.load(f)

            for order_data in sample_orders:
                # order_date를 datetime 형식으로 변환
                if isinstance(order_data.get('order_date'), str):
                    order_data['order_date'] = datetime.fromisoformat(order_data['order_date'])
                
                order = Order(**order_data)
                self.collect_order(order)
        except Exception as e:
            print(f"샘플 데이터를 로드하는데 실패했습니다. : {e}")

    def collect_order(self, order_data):
        try:
            # Order 객체가 아니면 변환
            if isinstance(order_data, dict):
                order_data = Order(**order_data)
            
            order_id = order_data.order_id
            
            if not order_id:
                print("주문 ID가 누락되었습니다.")
                return {'error': "주문 ID가 필요합니다."}, 400
            
            self.orders[order_id] = order_data

            # Order 객체를 dict로 변환해 외부 시스템 전송
            self.tms.send_order(order_data.to_dict())
            if hasattr(order_data, 'campaign_id'):
                self.tason.send_order(order_data.to_dict())

            return {"message": f"주문 {order_id}가 성공적으로 수집되었습니다."}, 200
        except (TypeError, ValueError) as e:
            print(f"주문 수집 중 에러 발생: {e}")
            return {'error': '유효하지 않은 주문 데이터 포맷'}, 400
        except Exception as e:
            print(f"주문 수집 중 예기치 못한 오류 발생: {e}")
            return {'error': "예상치 못한 오류"}, 500

    def update_order(self, order_data):
        try:
            if isinstance(order_data, dict):
                order_data = Order(**order_data)
            
            order_id = order_data.order_id

            if not order_id:
                return {'error': '주문 id가 필요합니다.'}, 400
            
            if order_id not in self.orders:
                self.orders[order_id] = order_data
            else:
                existing_order = self.orders[order_id]
                existing_order.order_status = order_data.order_status
                existing_order.items = order_data.items

            self.tms.send_order(order_data.to_dict())
            return {'message':f'주문 {order_id}가 성공적으로 업데이트되었습니다.'}, 200
        except (TypeError, ValueError) as e:
            print(f"업데이트 중 오류 발생 : {e}")
            return {'error':'유효하지 않은 데이터 형식'}, 400
        except Exception as e:
            print(f'업데이트 중 예기치 못한 오류 발생 : {e}')
            return {'error':'알 수 없는 오류 발생'}, 500

    def get_order(self, order_id):
        try:
            order = self.orders.get(order_id)
            if not order:
                return {'error':'주문을 찾을 수 없습니다.'}, 404
            return order.to_dict()
        except Exception as e:
            print(f'주문을 찾는 중 오류 발생: {e}')
            return {'error':'주문을 찾을 수 없습니다.'}, 500

    def list_orders(self):
        try:
            return [order.to_dict() for order in self.orders.values()]
        except Exception as e:
            print(f"주문 목록 조회 중 오류 발생: {e}")
            return {'error':'주문 목록을 조회할 수 없습니다.'}, 500
