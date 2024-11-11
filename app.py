from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

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
        
# 주문관리 시스템
class OrderService():
    def __init__(self):
        self.orders = {}
        self.tms = TMSInterface()
        self.tason = TasOnInterface()
        self._load_sample_orders()

    def _load_sample_orders(self):
        try:
            with open('sample_orders.json', 'r', encoding='utf-8') as f:
                sample_orders = json.load(f)

            for order_id, order_data in sample_orders.items():
                self.collect_order(order_data)
        except Exception as e:
            print(f"샘플 데이터를 로드하는데 실패했습니다. : {e}")
    
    def collect_order(self, order_data):
        try :
            order_id = order_data.get('order_id')

            if not order_id:
                return {'error': "주문 id가 필요합니다."}, 400
            
            self.orders[order_id] = order_data

            self.tms.send_order(order_data)
            
            if 'campaign_id' in order_data:
                self.tason.send_order(order_data)
            return {"message": f"주문{order_id} 가 성공적으로 수집되었습니다."}, 201
            
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
            
            if order_id not in self.orders:
                self.orders[order_id] = order_data
            else:
                self.orders[order_id].update(order_data)

            self.tms.send_order(order_data)
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
            return order
        except Exception as e:
            print(f'주문을 찾는 중 오류 발생: {e}')
            return {'error':'주문을 찾을 수 없습니다.'}, 500
        
    def list_orders(self):
        try:
            return  list(self.orders.values())
        except Exception as e:
            print(f"주문 목록 조회 중 오류 발생: {e}")
            return {'error':'주문 목록을 조회할 수 없습니다.'}, 500
        
    #flask 엔드 포인트
order_service = OrderService()

@app.route('/collect_order', methods=['POST'])
def collect_order():
    order_data  = request.json
    return jsonify(order_service.collect_order(order_data))

@app.route('/update_order', methods=['POST'])
def update_order():
    order_data = request.json  
    return jsonify(order_service.update_order(order_data))

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    return jsonify(order_service.get_order(order_id))

@app.route('/orders', methods=['GET'])
def list_orders():
    return jsonify(order_service.list_orders())

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0')