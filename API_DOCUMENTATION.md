# Tài liệu API Hệ thống Đặt món (tổng hợp từ @routes @controllers @dao @models)

## Base URL
```
http://127.0.0.1:5000
```

## Xác thực & Headers
- Khách hàng: OTP → JWT (access, refresh)
- Nhân viên/Chủ/Admin: username/password → JWT
- Header: `Authorization: Bearer <access_token>` cho endpoint cần bảo vệ
- Mẫu phản hồi chung: `{ success: boolean, message: string, data?: any }`

---

## 🔍 Tìm kiếm

### GET /api/search/
- Query: `q`, `lat`, `lon`, `min_price`, `max_price`, `sort_by` (distance|price), `sort_order` (asc|desc), `page`, `per_page`
- Response.data:
  - `items`: [
    restaurant.to_dict(include_sensitive=false) + `distance_km` + `searched_foods` (id, name, description, price, image_url, available)
  ]
  - `pagination`: { page, per_page, total, pages }

---

## 🍽️ Món ăn (Food)

### GET /api/food/
- Query: `category`, `available` (default true), `q`, `page`, `per_page`, `lat` (default 10.754792), `lon` (default 106.6952276), `max_km`, `seed_random`
- Response.data:
  - `items`: food.to_dict() mở rộng `distance_km` và `restaurant.distance_km` (nếu có)
  - `meta`: thông tin phân trang

### GET /api/food/{food_id}/
- Response.data: nếu có chi tiết mở rộng: `food.to_dict()` + `sold_count`, `avg_rating`, `review_count`, `recent_reviews` (tối đa 5), `restaurant`

### POST /api/food/
- Body: { name (required), price (required), description?, category?, image_url?, available?=true, restaurant_id? }
- Response: 201, `food.to_dict()`

### PUT /api/food/{food_id}/
- Body: { name?, description?, price?, category?, image_url?, available? }
- Response: `updated_food.to_dict()`

### DELETE /api/food/{food_id}/
- Response: message thành công

---

## 🏷️ Danh mục (Category)

### GET /api/category/
- Response.data: [{ id, name, description }]

---

## 🏪 Nhà hàng (Restaurant)

### GET /api/restaurant/public
- Query: `q`, `page`, `per_page`, `lat`, `lon`, `max_km`
- Response.data: { items: restaurant.to_dict()[], meta }

### GET /api/restaurant/{restaurant_id}/detail
- Response.data: restaurant.to_dict() + thống kê: `total_revenue`, `completed_orders`, `avg_rating`, `review_count`, `food_count`, `recent_reviews` (5), `top_foods` (id, name, price, image_url, total_sold)

---

## 🎟️ Mã giảm giá (Coupon)

### POST /api/coupon/
- Body: tối thiểu `code`, `discount_type` (percent|fixed); các trường khác theo model Coupon
- Response: 201, coupon.to_dict()

### POST /api/coupon/apply
- Body: { code (string), order_amount (number), restaurant_id? (int), food_ids? (int[]) }
- Response.data: { coupon: coupon.to_dict(), discount: number, payable: number }

### GET /api/coupon/
- Query: `restaurant_id` (optional)
- Response.data: coupon.to_dict()[] đang active

### GET /api/coupon/code/{code}
- Response.data: coupon.to_dict()

### GET /api/coupon/restaurant/{restaurant_id} (staff)
- Response.data: coupon.to_dict()[] theo nhà hàng

### POST /api/coupon/restaurant/{restaurant_id} (staff)
- Body: dữ liệu coupon; server gán `restaurant_id`
- Response: 201, coupon.to_dict()

### PUT /api/coupon/{coupon_id} (staff)
- Body: trường cập nhật
- Response: coupon.to_dict()

### DELETE /api/coupon/{coupon_id} (staff)
- Response: message

---

## 👤 Khách hàng (Customer)

### GET /api/customer/profile/
- JWT customer
- Response.data: customer.to_dict()

### PUT /api/customer/profile/
- Body: { full_name?, phone?, email?, address? }
- Response: message

### GET /api/customer/cart/
- Response.data: cấu trúc từ `CartDAO.get_cart_with_items_and_data(customer_id)`

### POST /api/customer/cart/add/
- Body: { food_id (required), quantity?=1, topping_ids? int[] }
- Response: message

### PUT /api/customer/cart/update/{item_id}/
- Body: { quantity >= 1 }
- Response: message

### DELETE /api/customer/cart/remove/{item_id}/
### DELETE /api/customer/cart/clear/
- Response: message

### GET /api/customer/orders/
- Query: `page`, `per_page`
- Response.data: { items: order.to_dict()[], pagination }

### GET /api/customer/orders/{order_id}/
- Response.data: order.to_dict()

### POST /api/customer/orders/
- Body: { delivery_address, delivery_phone, delivery_note?/note?, coupon_code? } (items lấy từ cart)
- Server sẽ tự kiểm tra và áp dụng mã giảm giá (nếu có): hiệu lực thời gian, ràng buộc nhà hàng, món áp dụng, giá trị tối thiểu, mức giảm tối đa. Tổng tiền được trừ trực tiếp trước khi lưu đơn.
- Response.data: order.to_dict() kèm, nếu có, `coupon_applied: { code, discount_amount }`

### PUT /api/customer/orders/{order_id}/cancel/
- Body: { reason }
- Response: message

### GET /api/customer/reviews/
- Query: `restaurant_id`?, `page`?, `per_page`?
- Response.data: { items: review.to_dict()[], pagination }

### POST /api/customer/reviews/
- JWT customer; Body: { food_id, rating (1..5), comment? }
- Điều kiện: đã mua món, chưa review
- Response: message

### POST /api/customer/payment/deposit/ (mock)
### POST /api/customer/payment/withdraw/ (mock)
- Body: { amount > 0 }
- Response.data: { new_balance }

---

## 👨‍💼 Nhân viên/Chủ (Staff)

Yêu cầu JWT + thuộc nhà hàng tương ứng.

### GET /api/staff/foods/
- Query: `page`, `per_page`
- Response.data: { items: food.to_dict()[], pagination }

### GET /api/staff/foods/{food_id}/
- Response.data: food.to_dict()

### POST /api/staff/foods/
### PUT /api/staff/foods/{food_id}/
### DELETE /api/staff/foods/{food_id}/
### PUT /api/staff/foods/{food_id}/toggle/
- Body (POST/PUT): { name, price, description?, image_url?, available? }
- Response: message hoặc food.to_dict()

### GET /api/staff/restaurant/
### PUT /api/staff/restaurant/
### PUT /api/staff/restaurant/hours/
### PUT /api/staff/restaurant/toggle/
- Body update: { name?, description?, phone?, email?, address?, image_url? } hoặc { opening_hours }
- Response: message hoặc restaurant.to_dict()

### GET /api/staff/orders/
- Query: `status`?; phân trang `page`, `per_page`
- Response.data: { items: order.to_dict()[], pagination }

### GET /api/staff/orders/{order_id}/
### PUT /api/staff/orders/{order_id}/accept/
### PUT /api/staff/orders/{order_id}/done/
### PUT /api/staff/orders/{order_id}/complete/
### PUT /api/staff/orders/{order_id}/cancel/
- Body cancel: { reason }
- Response: message hoặc order.to_dict()

### GET /api/staff/reviews/
- Response.data: { items: review.to_dict()[], pagination }

### GET /api/staff/revenue/
- Query: `start_date` (YYYY-MM-DD, default 30 ngày), `end_date` (YYYY-MM-DD, default hôm nay)
- Response.data: { total_revenue, order_count, period {start_date,end_date}, daily_revenue: [{ date, revenue, orders }] }

### GET /api/staff/profile/
### PUT /api/staff/profile/
- Body update: { full_name?, phone?, email?, address? }
- Response: message hoặc user.to_dict()

### POST /api/staff/payment/deposit/ (mock)
### POST /api/staff/payment/withdraw/ (mock)

---

## 🔐 Xác thực (Auth)

### POST /api/auth/staff/login/
- Body: { username, password }
- Response.data: { user: user.to_dict(), tokens }

### POST /api/auth/staff/register/
- Body bắt buộc: { first_name, last_name, phone, email, address, password, username, gender }
- Response: 201, user.to_dict() + { next_step: 'create_restaurant' }

### POST /api/auth/customer/send-otp/
- Body: { phone }
- Response.data: { otp }

### POST /api/auth/customer/verify-otp/
- Body: { phone, otp_code }
- Response.data: { customer: customer.to_dict(), tokens, is_new }

### POST /api/auth/refresh/
- Response.data: { access_token, token_type: 'Bearer' }

### GET /api/auth/profile/
### PUT /api/auth/profile/
- Body update: { first_name?, last_name?, address?, email?, gender?, date_of_birth?(YYYY-MM-DD) }
- Response: profile đã cập nhật

---

## 👨‍💻 Admin

### GET /api/admin/dashboard/
### GET /api/admin/users/ (role?)
### GET /api/admin/customers/
### GET /api/admin/orders/ (status?)
- Yêu cầu JWT + quyền admin
- Response.data: tuỳ theo controller (các bản ghi `to_dict()`)

---

## 🧾 Hoá đơn (Invoice)

### POST /api/invoice/
- Body bắt buộc: { order_id, payment_method, subtotal, tax, total }
- Response: 201, invoice.to_dict()

### GET /api/invoice/order/{order_id}/
- Response.data: invoice.to_dict()

---

## 🧾 Đơn hàng (Order public)

### POST /api/order/
- Body: { customer_id, items: [{ food_id, quantity, price? }], delivery_address?, delivery_phone?, notes? }
- Response: 201, order.to_dict()

### GET /api/order/{order_id}/
### GET /api/order/customer/{customer_id}/
### GET /api/order/restaurant/{restaurant_id}/
- Response.data: order.to_dict() hoặc danh sách

### PUT /api/order/{order_id}/status/
- Body: { status in [pending, confirmed, preparing, ready, delivering, delivered, cancelled] }
- Response.data: order.to_dict()

### POST /api/order/{order_id}/cancel/
- Body: { cancel_reason_id?, cancel_note? }
- Response.data: order.to_dict()

### PUT /api/order/{order_id}/assign-staff/{staff_id}/
- Response: message + order.to_dict()

---

## 💳 Thanh toán VNPay

### POST /api/payment/deposit/create/
- JWT base user
- Body: { amount > 0 }
- Response.data: { payment_url, order_id }

### GET /api/payment/vnpay/return/
- Response.data: { valid_signature, params, credited_by_return? }

### GET|POST /api/payment/vnpay/ipn/
- Trả về: { RspCode, Message }

### GET /api/payment/wallet/balance/
- JWT base user
- Response.data: { balance }

### POST /api/payment/order/pay/
- JWT customer; Body: { order_id }
- Response.data: nếu đủ ví: `{ paid_by_wallet, order_status: 'paid' }`; nếu không đủ: `{ payment_url, order_id, amount_wallet: 0, amount_vnpay }`

---

## 🔁 Luồng nghiệp vụ Đơn hàng & Thanh toán

- `pending`: khách tạo đơn (chưa thanh toán). Nhà hàng chưa nhìn thấy trong danh sách cần nhận.
- `paid`: khách thanh toán xong (wallet hoặc VNPay). Đơn chuyển cho nhà hàng, có thể bấm "accept".
- `accepted`: nhà hàng nhận đơn và chuẩn bị món. Tiền được ghi nhận cho owner.
- `done`: bếp đã xong, bàn giao vận chuyển.
- `completed`: giao hàng xong, khách đã nhận.
- `cancelled`: huỷ đơn; hoàn tiền nếu đã thanh toán.

Các API liên quan:
- Thanh toán: `POST /api/payment/order/pay/` (đủ ví → set `status=paid`; thiếu ví → tạo VNPay)
- Nhà hàng nhận đơn: `PUT /api/staff/orders/{order_id}/accept/` (chỉ khi `status=paid`)
- Đánh dấu xong món: `PUT /api/staff/orders/{order_id}/done/` (khi `status=accepted`)
- Hoàn tất: `PUT /api/staff/orders/{order_id}/complete/` (khi `status=done`)

---

## ⭐ Review công khai

### POST /api/review/
- Body: { customer_id, rating (1..5), ... }
- Response: 201, review.to_dict()

### GET /api/review/restaurant/{restaurant_id}/
### GET /api/review/food/{food_id}/
- Response.data: review.to_dict()[]

---

## 📦 Tóm tắt model (chính)
- Food: id, name, description, price, image_url, available, restaurant_id, created_at
- Restaurant: id, name, address, phone, email, description, image_url, latitude, longitude, is_active, opening_hours
- Order: id, customer_id, restaurant_id, total_amount, status, created_at, accepted_at?, completed_at?, cancelled_at?, cancel_reason?, notes
- OrderItem: id, order_id, food_id, quantity, price
- Review: id, customer_id, food_id, restaurant_id, rating, comment, created_at
- Coupon: id, code, discount_type, discount_value, max_discount_amount?, min_order_amount?, start_date?, end_date?, is_active, restaurant_id?, foods?
- Customer: id, phone, full_name?, email?, address?, balance?, total_orders, loyalty_points
- User: id, username, role, first_name, last_name, phone, email, address, balance?

---

## Mẫu phản hồi

### Thành công
```json
{ "success": true, "message": "...", "data": {} }
```

### Lỗi
```json
{ "success": false, "message": "..." }
```

### Phân trang
```json
{ "success": true, "message": "...", "data": { "items": [], "pagination": { "page": 1, "per_page": 10, "total": 100, "pages": 10 } } }
```

---

## Khởi chạy nhanh
```bash
pip install -r requirements.txt
python init_data.py
python server.py
```
Swagger:
- http://127.0.0.1:5000/apidocs/
- http://127.0.0.1:5000/apispec_1.json


