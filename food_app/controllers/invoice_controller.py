from food_app.dao.invoice_dao import InvoiceDAO
from food_app.utils.responses import success_response, error_response

class InvoiceController:
    @staticmethod
    def create_invoice(data):
        try:
            required = ['order_id', 'payment_method', 'subtotal', 'tax', 'total']
            if any(r not in data for r in required):
                return error_response('Thiếu thông tin hoá đơn', 400)
            invoice = InvoiceDAO.create_invoice(data)
            return success_response('Tạo hoá đơn thành công', invoice.to_dict(), 201)
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)

    @staticmethod
    def get_invoice_by_order(order_id):
        try:
            invoice = InvoiceDAO.get_invoice_by_order(order_id)
            if not invoice:
                return error_response('Không tìm thấy hoá đơn', 404)
            return success_response('Lấy hoá đơn thành công', invoice.to_dict())
        except Exception as e:
            return error_response(f'Lỗi server: {str(e)}', 500)


