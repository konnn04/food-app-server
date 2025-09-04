# Food App Server
![License](https://img.shields.io/github/license/konnn04/food-app-server?style=for-the-badge)
![Language](https://img.shields.io/badge/language-Python-blue?style=for-the-badge)
![Framework](https://img.shields.io/badge/framework-Flask-green?style=for-the-badge)

## 📖 Giới thiệu

**food-app-server** là backend API cho hệ thống đặt đồ ăn trực tuyến. Dự án được xây dựng bằng Flask và SQLAlchemy, hỗ trợ đầy đủ các chức năng quản lý nhà hàng, món ăn, đơn hàng, người dùng và thanh toán.

Hệ thống hỗ trợ nhiều vai trò người dùng: Admin, Owner (chủ nhà hàng), Manager, Staff và Customer, với các quyền hạn và chức năng phù hợp cho từng vai trò.

## 📂 Cấu trúc

```
food-app-server
├─ API_DOCUMENTATION.md
├─ config.py
├─ data_categories.json
├─ data_food.json
├─ food_app
│  ├─ admin
│  │  ├─ views.py
│  │  └─ __init__.py
│  ├─ controllers/*
│  ├─ dao/*
│  ├─ models
│  │  ├─ base_user.py
│  │  ├─ cancel_reason.py
│  │  ├─ cart.py
│  │  ├─ category.py
│  │  ├─ coupon.py
│  │  ├─ customer.py
│  │  ├─ food.py
│  │  ├─ food_categories.py
│  │  ├─ invoice.py
│  │  ├─ order.py
│  │  ├─ order_item.py
│  │  ├─ order_item_topping.py
│  │  ├─ otp.py
│  │  ├─ restaurant.py
│  │  ├─ restaurant_staff.py
│  │  ├─ review.py
│  │  ├─ topping.py
│  │  ├─ user.py
│  │  └─ __init__.py
│  ├─ routes
│  │  ├─ admin_api.py
│  │  ├─ auth.py
│  │  ├─ cart.py
│  │  ├─ coupon.py
│  │  ├─ customer.py
│  │  ├─ food.py
│  │  ├─ invoice.py
│  │  ├─ order.py
│  │  ├─ restaurant.py
│  │  ├─ review.py
│  │  ├─ search.py
│  │  └─ staff.py
│  ├─ templates
│  │  └─ admin
│  │     ├─ base.html
│  │     ├─ dashboard.html
│  │     ├─ login.html
│  │     └─ master.html
│  ├─ utils
│  │  ├─ cloudinary.py
│  │  ├─ decorators.py
│  │  ├─ distance.py
│  │  ├─ geocoding.py
│  │  ├─ jwt_service.py
│  │  ├─ mail.py
│  │  ├─ pagination.py
│  │  ├─ responses.py
│  │  ├─ sms.py
│  │  └─ validators.py
│  └─ __init__.py
├─ init_data.py
├─ requirements.txt
└─ server.py
```

## 🚀 Triển khai

Để triển khai dự án, bạn có thể sử dụng các lệnh sau:

```bash
# Tạo môi trường ảo Python
python -m venv .venv

# Kích hoạt môi trường ảo
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Cài đặt các phụ thuộc
pip install -r requirements.txt

# Khởi tạo dữ liệu mẫu
python init_data.py

# Chạy ứng dụng
python server.py
```

Sau khi khởi động, bạn có thể truy cập:
- API: http://127.0.0.1:5000/api/
- Admin Dashboard: http://127.0.0.1:5000/admin/
- API Documentation: http://127.0.0.1:5000/apidocs/

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp từ cộng đồng. Bạn có thể tạo pull request hoặc issue để báo cáo lỗi hoặc đề xuất tính năng mới.

## 📝 Giấy phép

Dự án này được cấp phép theo Giấy phép Apache 2.0. Vui lòng xem tệp LICENSE để biết thêm chi tiết.