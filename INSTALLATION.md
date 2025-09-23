# Hướng dẫn cài đặt Food App Server

Hướng dẫn này sẽ giúp bạn cài đặt và chạy Food App Server từ đầu đến cuối. Ứng dụng được xây dựng trên Python và Flask, sử dụng SQLAlchemy để tương tác với cơ sở dữ liệu.

## Mục lục

- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt môi trường](#cài-đặt-môi-trường)
- [Cấu hình môi trường](#cấu-hình-môi-trường)
- [Khởi tạo cơ sở dữ liệu](#khởi-tạo-cơ-sở-dữ-liệu)
- [Chạy ứng dụng](#chạy-ứng-dụng)
- [Truy cập API và Admin Panel](#truy-cập-api-và-admin-panel)
- [Xử lý sự cố](#xử-lý-sự-cố)

## Yêu cầu hệ thống

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn có các thành phần sau:

- Python 3.9 trở lên
- pip (trình quản lý gói Python)
- PostgreSQL (hoặc SQLite cho môi trường phát triển)
- Git (để clone repository)

## Cài đặt môi trường

### Bước 1: Clone repository

```bash
git clone https://github.com/konnn04/food-app-server.git
cd food-app-server
```

### Bước 2: Tạo môi trường ảo Python

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

Sau khi kích hoạt môi trường ảo, dấu nhắc lệnh của bạn sẽ có tiền tố `(.venv)` cho biết môi trường ảo đã được kích hoạt.

### Bước 3: Cài đặt các gói phụ thuộc

```bash
pip install -r requirements.txt
```

## Cấu hình môi trường

### Bước 1: Tạo file .env

Tạo file `.env` trong thư mục gốc của dự án với nội dung sau (thay thế các giá trị theo môi trường của bạn):

```
# Cấu hình Flask
FLASK_ENV=development
SECRET_KEY=your-very-secret-key-here

# Cấu hình Database
DATABASE_URL=postgresql://username:password@localhost/food_app_db
# Hoặc sử dụng SQLite (mặc định):
# DATABASE_URL=sqlite:///food_ordering.db

# Cấu hình JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Cấu hình Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=Food App <no-reply@foodapp.com>

# Cấu hình VNPay (nếu sử dụng)
VNPAY_TMN_CODE=your-vnpay-tmn-code
VNPAY_HASH_SECRET=your-vnpay-hash-secret
VNPAY_PAYMENT_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:5000/api/payment/vnpay/return/
VNPAY_IPN_URL=http://localhost:5000/api/payment/vnpay/ipn/
```

### Bước 2: Cấu hình cơ sở dữ liệu

Nếu bạn sử dụng PostgreSQL, hãy tạo cơ sở dữ liệu:

```bash
# Đăng nhập vào PostgreSQL
psql -U postgres

# Tạo database
CREATE DATABASE food_app_db;

# Tạo user và cấp quyền (tùy chọn)
CREATE USER food_app WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE food_app_db TO food_app;

# Thoát
\q
```

Đảm bảo thông tin kết nối đã được cập nhật đúng trong file `.env`.

## Khởi tạo cơ sở dữ liệu

### Bước 1: Khởi tạo schema

Ứng dụng sẽ tự động tạo các bảng cơ sở dữ liệu khi chạy lần đầu tiên. Tuy nhiên, bạn cũng có thể khởi tạo thủ công bằng cách chạy:

```bash
python -c "from food_app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Bước 2: Khởi tạo dữ liệu mẫu

Để khởi tạo dữ liệu mẫu bao gồm người dùng, nhà hàng, món ăn, và các danh mục, chạy lệnh sau:

```bash
python init_data.py
```

Quá trình này có thể mất vài phút tùy thuộc vào lượng dữ liệu mẫu.

## Chạy ứng dụng

### Khởi chạy server

```bash
python server.py
```

Server mặc định sẽ chạy tại địa chỉ http://0.0.0.0:5000/

## Truy cập API và Admin Panel

### API Documentation

API documentation có thể được truy cập tại:
```
http://localhost:5000/apidocs/
```

### Admin Panel

Truy cập Admin Panel tại:
```
http://localhost:5000/admin/
```

Đăng nhập bằng tài khoản admin được tạo từ script khởi tạo dữ liệu:
- Username: admin@foodapp.com
- Password: admin123

## Triển khai Production

Để triển khai trong môi trường production, hãy thay đổi cấu hình trong file `.env`:

```
FLASK_ENV=production
```

Đồng thời, nên sử dụng một server WSGI như Gunicorn để chạy ứng dụng:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## Xử lý sự cố

### Lỗi kết nối cơ sở dữ liệu

- Kiểm tra kết nối PostgreSQL
- Đảm bảo DATABASE_URL trong file .env được cấu hình đúng
- Kiểm tra quyền truy cập của người dùng database

### Lỗi khởi tạo dữ liệu

Nếu bạn gặp lỗi khi chạy `init_data.py`, có thể thử:

```bash
# Xóa database hiện tại và tạo lại
python -c "from food_app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"

# Sau đó chạy lại
python init_data.py
```

### Lỗi gửi email

- Kiểm tra cấu hình SMTP trong file .env
- Nếu bạn sử dụng Gmail, đảm bảo đã bật "Cho phép ứng dụng kém an toàn" hoặc tạo "App Password"

### Lỗi thanh toán VNPay

- Kiểm tra thông tin kết nối VNPay trong file .env
- Đảm bảo đã cấu hình đúng các callback URL trong tài khoản VNPay của bạn

## Tùy chỉnh nâng cao

### Cấu hình Cloudinary (nếu sử dụng để lưu trữ hình ảnh)

Thêm vào file `.env`:

```
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Cấu hình Google Maps API (cho tính năng geolocation)

Thêm vào file `.env`:

```
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

### Cấu hình SMS (nếu sử dụng)

Thêm vào file `.env`:

```
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
```