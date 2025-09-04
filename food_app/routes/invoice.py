from flask import Blueprint, request
from food_app.controllers.invoice_controller import InvoiceController
from flasgger import swag_from

invoice_bp = Blueprint('invoice', __name__)

@invoice_bp.route('/', methods=['POST'])
@swag_from({'tags': ['Invoice'], 'summary': 'Create invoice'})
def create_invoice():
    data = request.get_json()
    return InvoiceController.create_invoice(data)

@invoice_bp.route('/order/<int:order_id>/', methods=['GET'])
@swag_from({'tags': ['Invoice'], 'summary': 'Get invoice by order id'})
def get_invoice(order_id):
    return InvoiceController.get_invoice_by_order(order_id)


