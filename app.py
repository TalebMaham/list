from flask import Flask, render_template, jsonify, request
import logging

import json
import requests
# from cashier_class import cashier

app = Flask(__name__)


# Configurer le journalisation
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

@app.route('/')
def index():
    API_URL = 'https://www.chri2.com/api/products/'
    try : 
        response = requests.get(API_URL)
        if response.status_code == 200:
            products = response.json()
        else:
            products = []
    except Exception as e  : 
        print(e)
    return render_template('index.html', products=products)

# @app.route('/start_transaction', methods=['POST'])
# def start_transaction():
#     try:
#         total = request.json.get('total')
#         print(f"le totale est : {total} ")
#         cashier.accepter()
#         cashier.compting = True
#         cashier.total = total
#         # Simuler une transaction ici
#         return jsonify({"message": "Transaction started", "total": total}), 200
#     except Exception as e:
#         logging.error(f"Error starting transaction: {e}")
#         return jsonify({"error": str(e)}), 500
    
# @app.route('/get_inserted_amount', methods=['GET'])
# def get_inserted_amount():
#     # Simuler le montant inséré pour la démonstration
#     montant_insere = cashier.get_total_inserted_amount()
#     finish = cashier.get_is_finish()
#     return jsonify({"montant_insere": montant_insere, "finish" :finish })




if __name__ == '__main__':
    app.run()
