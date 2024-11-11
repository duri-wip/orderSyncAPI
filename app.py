from flask import Flask, request, jsonify

from src.OrderService import OrderService

app = Flask(__name__)
       
order_service = OrderService()

@app.route('/collect_order', methods=['POST'])
def collect_order():
    order_data  = request.json
    response = order_service.collect_order(order_data)
    return jsonify(response[0]), response[1]

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