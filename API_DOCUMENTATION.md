# Food Ordering System API Documentation

## Base URL
```
http://127.0.0.1:5000
```

## Authentication
- **Customer**: OTP-based authentication
- **Staff/Admin**: JWT token authentication
- **Headers**: `Authorization: Bearer <token>` (for protected endpoints)

---

## 🔍 Search Endpoints

### Search Food and Restaurants
```
GET /api/search/
```
**Description**: Primary search endpoint for finding restaurants and food items

**Query Parameters**:
- `q` (string): Search keyword for food or restaurant name
- `lat` (float): Current latitude
- `lon` (float): Current longitude  
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter
- `sort_by` (string): Sort by "distance" or "price"
- `sort_order` (string): Sort order "asc" or "desc"
- `page` (integer): Page number
- `per_page` (integer): Items per page

**Response**: List of restaurants with up to 3 related food items per restaurant

---

## 🍽️ Food Endpoints

### List Foods
```
GET /api/food/
```
**Description**: Get list of food items with filtering and pagination

**Query Parameters**:
- `category` (integer): Filter by category ID
- `available` (boolean): Filter by availability
- `q` (string): Search keyword
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `lat` (float): Current latitude (default: 10.754792)
- `lon` (float): Current longitude (default: 106.6952276)
- `max_km` (float): Maximum distance in kilometers

### Get Food Detail
```
GET /api/food/{food_id}/
```
**Description**: Get detailed food information with statistics

### Create Food (Staff)
```
POST /api/food/
```
**Description**: Create new food item (Staff only)

### Update Food (Staff)
```
PUT /api/food/{food_id}/
```
**Description**: Update food information (Staff only)

### Delete Food (Staff)
```
DELETE /api/food/{food_id}/
```
**Description**: Delete food item (Staff only)

---

## 🏪 Restaurant Endpoints

### List Restaurants (Public)
```
GET /api/restaurant/public
```
**Description**: Public list of restaurants with pagination and geo filtering

**Query Parameters**:
- `q` (string): Search keyword
- `page` (integer): Page number
- `per_page` (integer): Items per page
- `lat` (float): Current latitude
- `lon` (float): Current longitude
- `max_km` (float): Maximum distance in kilometers

### Get Restaurant Detail
```
GET /api/restaurant/{restaurant_id}/detail
```
**Description**: Get detailed restaurant information with statistics

---

## 👤 Customer Endpoints

### Cart Management

#### Get Cart
```
GET /api/customer/cart/
```
**Description**: Get customer's cart items

#### Add to Cart
```
POST /api/customer/cart/add/
```
**Description**: Add food item to cart

#### Update Cart Item
```
PUT /api/customer/cart/update/{item_id}/
```
**Description**: Update quantity of cart item

#### Remove Cart Item
```
DELETE /api/customer/cart/remove/{item_id}/
```
**Description**: Remove item from cart

#### Clear Cart
```
DELETE /api/customer/cart/clear/
```
**Description**: Clear entire cart

### Order Management

#### List Orders
```
GET /api/customer/orders/
```
**Description**: Get customer's order history

#### Create Order
```
POST /api/customer/orders/
```
**Description**: Place new order from cart

#### Get Order Detail
```
GET /api/customer/orders/{order_id}/
```
**Description**: Get detailed order information

#### Cancel Order
```
PUT /api/customer/orders/{order_id}/cancel/
```
**Description**: Cancel existing order

### Payment (Mockup)

#### Deposit Money
```
POST /api/customer/payment/deposit/
```
**Description**: Deposit money to account (mockup)

#### Withdraw Money
```
POST /api/customer/payment/withdraw/
```
**Description**: Withdraw money from account (mockup)

### Profile Management

#### Get Profile
```
GET /api/customer/profile/
```
**Description**: Get customer profile information

#### Update Profile
```
PUT /api/customer/profile/
```
**Description**: Update customer profile

### Reviews

#### List Reviews
```
GET /api/customer/reviews/
```
**Description**: Get reviews for food items

#### Create Review
```
POST /api/customer/reviews/
```
**Description**: Create new review for food item (requires purchase verification)

---

## 👨‍💼 Staff Endpoints

### Food Management

#### List Restaurant Foods
```
GET /api/staff/foods/
```
**Description**: Get list of foods for staff's restaurant

#### Get Food Detail
```
GET /api/staff/foods/{food_id}/
```
**Description**: Get detailed food information

#### Create Food
```
POST /api/staff/foods/
```
**Description**: Create new food item

#### Update Food
```
PUT /api/staff/foods/{food_id}/
```
**Description**: Update food information

#### Delete Food
```
DELETE /api/staff/foods/{food_id}/
```
**Description**: Delete food item

#### Toggle Food Availability
```
PUT /api/staff/foods/{food_id}/toggle/
```
**Description**: Enable/disable food item

### Restaurant Management

#### Get Restaurant Info
```
GET /api/staff/restaurant/
```
**Description**: Get restaurant information

#### Update Restaurant Info
```
PUT /api/staff/restaurant/
```
**Description**: Update restaurant information

#### Update Opening Hours
```
PUT /api/staff/restaurant/hours/
```
**Description**: Update restaurant opening hours

#### Toggle Restaurant Status
```
PUT /api/staff/restaurant/toggle/
```
**Description**: Enable/disable restaurant

### Order Management

#### List Restaurant Orders
```
GET /api/staff/orders/
```
**Description**: Get orders for staff's restaurant

**Query Parameters**:
- `status` (string): Filter by order status

#### Get Order Detail
```
GET /api/staff/orders/{order_id}/
```
**Description**: Get detailed order information

#### Accept Order
```
PUT /api/staff/orders/{order_id}/accept/
```
**Description**: Accept incoming order

#### Complete Order
```
PUT /api/staff/orders/{order_id}/complete/
```
**Description**: Mark order as completed

#### Cancel Order
```
PUT /api/staff/orders/{order_id}/cancel/
```
**Description**: Cancel order with reason

### Reviews

#### List Restaurant Reviews
```
GET /api/staff/reviews/
```
**Description**: Get reviews for staff's restaurant

### Revenue

#### Get Revenue Statistics
```
GET /api/staff/revenue/
```
**Description**: Get revenue statistics

**Query Parameters**:
- `start_date` (string): Start date for statistics
- `end_date` (string): End date for statistics

### Profile Management

#### Get Staff Profile
```
GET /api/staff/profile/
```
**Description**: Get staff profile information

#### Update Staff Profile
```
PUT /api/staff/profile/
```
**Description**: Update staff profile

### Payment (Mockup)

#### Deposit Money
```
POST /api/staff/payment/deposit/
```
**Description**: Deposit money to account (mockup)

#### Withdraw Money
```
POST /api/staff/payment/withdraw/
```
**Description**: Withdraw money from account (mockup)

---

## 🔐 Authentication Endpoints

### Customer Authentication

#### Send OTP
```
POST /api/auth/customer/send-otp/
```
**Description**: Send OTP to customer phone number

**Request Body**:
```json
{
  "phone": "string"
}
```

#### Verify OTP
```
POST /api/auth/customer/verify-otp/
```
**Description**: Verify OTP and login customer

**Request Body**:
```json
{
  "phone": "string",
  "otp": "string"
}
```

### Staff/Admin Authentication

#### Staff Login
```
POST /api/auth/staff/login/
```
**Description**: Staff/admin login with username and password

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

#### Create Owner Account
```
POST /api/auth/staff/register/
```
**Description**: Create new owner/staff account

**Request Body**:
```json
{
  "username": "string",
  "password": "string",
  "full_name": "string",
  "email": "string",
  "phone": "string"
}
```

#### Refresh Token
```
POST /api/auth/refresh/
```
**Description**: Refresh access token using refresh token

---

## 👨‍💻 Admin Endpoints

### Dashboard
```
GET /api/admin/dashboard/
```
**Description**: Get overview data for admin dashboard

### User Management
```
GET /api/admin/users/
```
**Description**: Get list of all users

### Customer Management
```
GET /api/admin/customers/
```
**Description**: Get list of all customers

### Order Management
```
GET /api/admin/orders/
```
**Description**: Get all orders across all restaurants

---

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "error": "Error code"
}
```

### Paginated Response
```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": {
    "items": [...],
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10
  }
}
```

---

## 🔧 Special Features

### Order Logic
- **Opening Hours Check**: Orders cannot be placed when restaurant is closed
- **Food Availability**: Orders cannot include unavailable food items
- **Distance Calculation**: Uses Haversine formula for accurate distance calculation
- **Order Status Flow**: `pending` → `accepted` → `completed` or `cancelled`

### Review System
- **Food-based Reviews**: Reviews are tied to specific food items
- **Purchase Verification**: Customers must have purchased the food item before reviewing
- **Duplicate Prevention**: One review per food item per customer

### Payment System (Mockup)
- **Balance Management**: Track customer and staff balances
- **Deposit/Withdraw**: Simulate money transactions
- **Order Payment**: Deduct from balance when placing orders

### Search Features
- **Keyword Search**: Search by food name or restaurant name
- **Location-based**: Sort by distance from current coordinates
- **Price Filtering**: Filter by price range
- **Restaurant Grouping**: Group food items by restaurant

### Data Protection
- **Sensitive Data**: Tax codes and internal data hidden from public endpoints
- **Role-based Access**: Different endpoints for different user roles
- **JWT Security**: Secure token-based authentication

---

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python init_data.py
   ```

3. **Run Server**:
   ```bash
   python server.py
   ```

4. **Access API Documentation**:
   - Swagger UI: `http://127.0.0.1:5000/apidocs/`
   - API Spec: `http://127.0.0.1:5000/apispec_1.json`

---

## 📝 Notes for Frontend Development

- All timestamps are in ISO format
- Coordinates use decimal degrees (latitude, longitude)
- Prices are in the base currency unit
- File uploads support: PNG, JPG, JPEG, GIF, WEBP (max 16MB)
- Pagination defaults: page=1, per_page=10
- Maximum delivery distance: 20km
- Rating scale: 1-5 stars
