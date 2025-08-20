import requests
import dotenv
from config import Config

dotenv.load_dotenv()

import requests
from dotenv import dotenv_values

def send_otp_sms(phone, otp_code):
    try:
        # Lấy API key từ file .env
        config = dotenv_values(".env")
        api_key = config.get("TINGTINGDEV_API_KEY")
        sender = "TingTing"
        message = f"Mã xác thực của bạn là: {otp_code}. Mã có hiệu lực trong 5 phút."
        url = "https://v1.tingting.im/api/sms"

        payload = {
            "to": phone,               
            "content": message,
            "sender": sender
        }

        headers = {
            "Content-Type": "application/json",
            "apikey": api_key
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200 and data.get("status") == "success":
            print(f"✅ SMS sent to {phone}: {message}")
            print(f"📦 Transaction ID: {data.get('tranId')}")
            return True
        else:
            print(f"❌ Gửi OTP thất bại: {data}")
            return False

    except Exception as e:
        print(f"❌ SMS error: {str(e)}")
        return False

    

