from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import os


class EmailService:
    @staticmethod
    def send_email(to_email, subject, template_name, context=None):
        """
        Send an email using a template
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            template_name (str): Name of the template file (without extension)
            context (dict): Data to render in the template
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if context is None:
            context = {}
            
        try:
            # Get email configuration from app config
            smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('SMTP_PORT', 587)
            smtp_username = current_app.config.get('SMTP_USERNAME', '')
            smtp_password = current_app.config.get('SMTP_PASSWORD', '')
            from_email = current_app.config.get('FROM_EMAIL', smtp_username)
            
            # Debug logging
            current_app.logger.info(f"Email sending attempt - To: {to_email}, Subject: {subject}")
            current_app.logger.info(f"SMTP settings - Server: {smtp_server}, Port: {smtp_port}, Username: {smtp_username}")
            
            # Check if email config is valid
            if not smtp_username or not smtp_password:
                current_app.logger.warning("Missing SMTP credentials in configuration. Check your config.py or environment variables.")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Load template
            template_path = os.path.join(
                current_app.root_path, 
                'templates', 
                'emails', 
                f'{template_name}.html'
            )
            
            # Check if template exists
            if not os.path.exists(template_path):
                current_app.logger.error(f"Email template not found: {template_path}")
                return False
                
            with open(template_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
            
            # Render template
            template = Template(template_content)
            html_content = template.render(**context)
            
            # Attach HTML content
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                current_app.logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
                server.set_debuglevel(1)  # Enable debug output
                server.starttls()
                if smtp_username and smtp_password:
                    current_app.logger.info(f"Attempting to login with username: {smtp_username}")
                    server.login(smtp_username, smtp_password)
                current_app.logger.info(f"Sending email from {from_email} to {to_email}")
                server.sendmail(from_email, to_email, msg.as_string())
                current_app.logger.info("Email sent successfully")
                
            return True
        
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return False

    @staticmethod
    def send_order_confirmation(order, customer_email):
        """Send order confirmation email to customer"""
        context = {
            'order_id': order.id,
            'customer_name': f"{order.customer.first_name} {order.customer.last_name}",
            'restaurant_name': order.restaurant.name,
            'order_items': [item.to_dict() for item in order.items],
            'total_amount': order.total_amount,
            'order_date': order.created_at.strftime('%Y-%m-%d %H:%M')
        }
        
        return EmailService.send_email(
            to_email=customer_email,
            subject=f"[Food App] Đơn hàng #{order.id} đã được đặt thành công",
            template_name="order_confirmation",
            context=context
        )
    
    @staticmethod
    def send_payment_confirmation(order, customer_email):
        """Send payment confirmation email to customer"""
        import datetime
        context = {
            'order_id': order.id,
            'customer_name': f"{order.customer.first_name} {order.customer.last_name}",
            'restaurant_name': order.restaurant.name,
            'order_items': [item.to_dict() for item in order.items],
            'total_amount': order.total_amount,
            'payment_method': getattr(order, 'payment_method', 'Online'),
            'payment_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        }
        
        return EmailService.send_email(
            to_email=customer_email,
            subject=f"[Food App] Thanh toán cho đơn hàng #{order.id} thành công",
            template_name="payment_confirmation",
            context=context
        )
    
    @staticmethod
    def send_order_completion(order, customer_email):
        """Send order completion email to customer"""
        import datetime
        context = {
            'order_id': order.id,
            'customer_name': f"{order.customer.first_name} {order.customer.last_name}",
            'restaurant_name': order.restaurant.name,
            'order_items': [item.to_dict() for item in order.items],
            'total_amount': order.total_amount,
            'order_date': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'completed_date': order.completed_at.strftime('%Y-%m-%d %H:%M') if hasattr(order, 'completed_at') and order.completed_at else datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        }
        
        return EmailService.send_email(
            to_email=customer_email,
            subject=f"[Food App] Đơn hàng #{order.id} đã hoàn thành",
            template_name="order_completion",
            context=context
        )
    
    @staticmethod
    def send_restaurant_order_completion(order, restaurant_email):
        """Send order completion notification to restaurant owner"""
        import datetime
        context = {
            'order_id': order.id,
            'customer_name': f"{order.customer.first_name} {order.customer.last_name}",
            'restaurant_name': order.restaurant.name,
            'order_items': [item.to_dict() for item in order.items],
            'total_amount': order.total_amount,
            'order_date': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'completed_date': order.completed_at.strftime('%Y-%m-%d %H:%M') if hasattr(order, 'completed_at') and order.completed_at else datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        }
        
        return EmailService.send_email(
            to_email=restaurant_email,
            subject=f"[Food App] Đơn hàng #{order.id} đã hoàn thành",
            template_name="restaurant_order_completion",
            context=context
        )
