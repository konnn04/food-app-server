from flask import Blueprint, request
from flasgger import swag_from
from food_app.utils.responses import success_response, error_response
from food_app.utils.mail import EmailService

test_bp = Blueprint('test', __name__)

@test_bp.route('/test-email', methods=['GET'])
@swag_from({'tags': ['Test'], 'summary': 'Test email functionality'})
def test_email():
    """Test email sending functionality"""
    try:
        recipient = request.args.get('to', 'test@example.com')
        
        # Simple test context
        context = {
            'order_id': 123,
            'customer_name': 'Test Customer',
            'restaurant_name': 'Test Restaurant',
            'order_items': [
                {'food': {'name': 'Test Food'}, 'quantity': 2, 'unit_price': 50000}
            ],
            'total_amount': 100000,
            'order_date': '2025-09-24 15:30',
            'payment_method': 'Ví điện tử',
            'payment_date': '2025-09-24 15:35',
            'completed_date': '2025-09-24 16:00'
        }
        
        # Try to send all types of emails
        order_confirm = EmailService.send_email(
            to_email=recipient,
            subject="[Test] Order Confirmation",
            template_name="order_confirmation",
            context=context
        )
        
        payment_confirm = EmailService.send_email(
            to_email=recipient,
            subject="[Test] Payment Confirmation",
            template_name="payment_confirmation",
            context=context
        )
        
        order_complete = EmailService.send_email(
            to_email=recipient,
            subject="[Test] Order Completion",
            template_name="order_completion",
            context=context
        )
        
        restaurant_notify = EmailService.send_email(
            to_email=recipient,
            subject="[Test] Restaurant Notification",
            template_name="restaurant_order_completion",
            context=context
        )
        
        results = {
            'order_confirmation': order_confirm,
            'payment_confirmation': payment_confirm,
            'order_completion': order_complete,
            'restaurant_notification': restaurant_notify
        }
        
        return success_response('Email test results', results)
    except Exception as e:
        return error_response(f'Error testing emails: {str(e)}', 500)