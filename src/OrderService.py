import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
from dataclasses import asdict

from Order import Order
from ExternalSystemInterface import TMSInterface, TasOnInterface

# 주문관리 시스템
class OrderService():
    def __init__(self):
        self.orders = {}
        self.tms = TMSInterface()
        self.tason = TasOnInterface()
        self._load_sample_orders()

    def _load_sample_orders(self):
        try:
            with open('/home/sw/orderSyncAPI/data/sample_orders.json', 'r', encoding='utf-8') as f:
                sample_orders = json.load(f)

            for order_data in sample_orders:
                if isinstance(order_data.get('order_date'), str):
                    order_data['order_date'] = datetime.fromisoformat(order_data['order_date'])

                order = Order(**order_data)
                self.collect_order(order)
        except Exception as e:
            print(f"샘플 데이터를 로드하는데 실패했습니다. : {e}")
    
    def collect_order(self, order_data):
        try :
            if isinstance(order_data, dict):
                if isinstance(order_data.get('order_date'), str):
                    order_data['order_date'] = datetime.fromisoformat(order_data['order_date'])
                order_data = Order(**order_data)

            order_id = order_data.order_id
            
            if not order_id:
                return {'error': "주문 id가 필요합니다."}, 400
            
            self.orders[order_id] = order_data

            self.tms.send_order(order_data.to_dict())
            
            if hasattr(order_data, 'campaign_id'):
                self.tason.send_order(order_data.to_dict())

            return {"message": f"주문{order_id} 가 성공적으로 수집되었습니다."}, 200
            
        except (TypeError, ValueError) as e:
            print(f"주문 수집 중 에러 발생 : {e}")
            return {'error':'유효하지 않은 주문 데이터 포맷'}, 400
        except Exception as e:
            print(f"주문 수집 중 예쌍치 못한 오류 발생 : {e}")
            return {'error': "예상치 못한 오류"}, 500
    
    def update_order(self, order_data):
        try:
            order_id = order_data.get('order_id')

            if not order_id:
                return {'error': '주문 id가 필요합니다.'}, 400

            existing_order = self.orders.get(order_id)
            if not existing_order:
                return {'error': '주문을 찾을 수 없습니다.'}, 404

            # 필수 필드 채우기 (기존 필드를 유지하며 업데이트)
            updated_order_data = {
                'order_id': order_id,
                'customer_id': existing_order.customer_id,
                'customer_name': existing_order.customer_name,
                'order_date': existing_order.order_date,
                'order_status': order_data.get('order_status', existing_order.order_status),
                'campaign_id': existing_order.campaign_id,
                'items': order_data.get('items', existing_order.items),
            }

            updated_order = Order(**updated_order_data)
            self.orders[order_id] = updated_order

            self.tms.send_order(updated_order.to_dict())
            return {'message': f'주문 {order_id} 가 성공적으로 업데이트되었습니다.'}, 200
        except (TypeError, ValueError) as e:
            print(f"업데이트 중 오류 발생 : {e}")
            return {'error': '유효하지 않은 데이터 형식'}, 400
        except Exception as e:
            print(f'업데이트 중 예기치 못한 오류 발생 : {e}')
            return {'error': '알 수 없는 오류 발생'}, 500
        
    def get_order(self, order_id):
        try:
            order = self.orders.get(order_id)
            if not order:
                return {'error':'주문을 찾을 수 없습니다.'}, 404
            return order.to_dict(), 200
        except Exception as e:
            print(f'주문을 찾는 중 오류 발생: {e}')
            return {'error':'주문을 찾을 수 없습니다.'}, 500
        
    def list_orders(self):
        try:
            orders = [order.to_dict() for order in self.orders.values()]
            return  orders, 200
        except Exception as e:
            print(f"주문 목록 조회 중 오류 발생: {e}")
            return {'error':'주문 목록을 조회할 수 없습니다.'}, 500