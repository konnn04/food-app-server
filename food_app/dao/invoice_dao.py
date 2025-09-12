from food_app import db
from food_app.models.invoice import Invoice

class InvoiceDAO:
    @staticmethod
    def create_invoice(data):
        invoice = Invoice(**data)
        db.session.add(invoice)
        db.session.commit()
        return invoice

    @staticmethod
    def get_invoice_by_order(order_id):
        return Invoice.query.filter_by(order_id=order_id).first()


