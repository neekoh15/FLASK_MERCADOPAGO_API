from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

import json, pprint

import mercadopago

from ngrok_config import NGROK_FORWARD

#THIS IS COMMENTED BECAUSE AT THE TIME I IMPLEMENTED THE NGROK SERVICE WAS DOWN.
#INIT NGROK FORWARDING 
#ngrok_forward = NGROK_FORWARD()
#ngrok_forward.start_listener()
#ngrok_forward_url = ngrok_forward.listener.url()

#INIT MERCADOPAGO SDK
MERCADOPAGO_ACCESS_TOKEN = json.load(open('config.json', 'r')).get('MERCADOPAGO_TEST_ACCESS_TOKEN')
mercadopago_sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)

#INIT FLASK APP
app = Flask(__name__)
CORS(app)

flask_endpoints = {
    "homepage": "/",
    "mercado_pago_notificaciones": "/notificaciones",
    "mercado_pago_success": "/success",
    "mercado_pago_failure": "/failure",
    "mercado_pago_pending": "/pending"
}


def generar_preference() -> dict :

    test_item = {
        "id": "<YOUR-ITEM-ID>",
        "title": "<YOUR-ITEM-TITLE>",
        "quantity": 1,
        "unit_price": 50
    }
    
    items = [test_item]    

    back_urls = {
        "success": flask_endpoints["mercado_pago_success"],
        "failure": flask_endpoints["mercado_pago_failure"],
        "pending": flask_endpoints["mercado_pago_pending"]
    }

    #SET UP NGROK FORWARDING URL
    #notification_url = ngrok_forward_url + flask_endpoints["mercado_pago_notificaciones"]

    #USING VS CODE FORWARD PORT BECAUSE NGROK WAS DOWN
    #TO CONFIG THIS PORT GO TO > PORTS > ADD PORT > PORT 7500 > AND SET VISIBILITY TO "PUBLIC" OTHERWISE IT WILL NOT WORK.
    vscode_forward_port = "<YOUR VS CODE FORWARD PORT>"
    notification_url = vscode_forward_port + flask_endpoints["mercado_pago_notificaciones"]

    preference_content = {
        "items":items,
        "back_urls": back_urls,
        "notification_url": notification_url
    }

    preference = mercadopago_sdk.preference().create(preference_content)

    pprint.pprint(preference)

    return preference

def get_link_de_pago() -> str:
    return generar_preference().get("response").get("init_point")


@app.route(flask_endpoints["homepage"])
def homepage():
    link_de_pago = get_link_de_pago()
    #print('link de pago: ', link_de_pago)

    return render_template("index.html", link_de_pago=link_de_pago)
    #return {"link_de_pago": link_de_pago} #FOR API MODE

@app.route(flask_endpoints["mercado_pago_notificaciones"], methods=["POST", "GET"])
def recibir_notificacion():
    #agarrar username e itemid
    #notificacion = request.get_json()
    data = request.get_data()

    pprint.pprint(data)

    merchant_order_id = request.args.get('id')
    topic = request.args.get('topic')

    if topic == 'merchant_order':
        merchant_order:dict = mercadopago_sdk.merchant_order().get(merchant_order_id)

        pprint.pprint(merchant_order)

        if merchant_order.get('response').get('status') == 'closed':
            preference_id = merchant_order.get('response').get('preference_id')

            payments = merchant_order.get('response').get('payments')
            items = merchant_order.get('response').get('items')

            ammount_paid = 0
            for payment in payments:
                ammount_paid += payment.get('transaction_amount')

            items_total_cost = 0
            for item in items:
                items_total_cost += item.get('quantity') * item.get('unit_price')


            if ammount_paid >= items_total_cost:
                print('PAGO EXITOSO')


        
    return {"status": 200}, 200

if __name__ == '__main__':
    HOST = json.load(open('config.json', 'r')).get('HOST')
    PORT = json.load(open('config.json', 'r')).get('PORT')

    app.run(host=HOST, port=PORT, debug=True)


