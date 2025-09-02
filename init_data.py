import os
import sys
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal

from food_app.models.cart import Cart, CartItem
from food_app.models.review import Review

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from food_app import create_app, db
from food_app.models import *

def load_food_data():
    """Load food data from JSON files"""
    with open('data_food.json', 'r', encoding='utf-8') as f:
        food_data = json.load(f)
    
    with open('data_categories.json', 'r', encoding='utf-8') as f:
        categories_data = json.load(f)
    
    return food_data, categories_data

def create_sample_data():
    app = create_app()
    
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        # Load food and categories data
        food_data, categories_data = load_food_data()
        
        print("Creating categories...")
        categories = {}
        for cat_data in categories_data:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description']
            )
            db.session.add(category)
            db.session.flush()  # Get the ID
            categories[cat_data['id']] = category
        
        print("Creating cancel reasons...")
        cancel_reasons = []
        reasons = [
            "Khách hàng yêu cầu hủy",
            "Nhà hàng không thể phục vụ",
            "Thời gian giao hàng quá lâu",
            "Sản phẩm hết hàng",
            "Lý do khác"
        ]
        for reason in reasons:
            cancel_reason = CancelReason(name=reason)
            db.session.add(cancel_reason)
            cancel_reasons.append(cancel_reason)
        
        print("Creating users...")
        users = []
        user_data = [
            {"username": "admin", "email": "admin@foodapp.com", "password": "admin123", "role": "admin"},
            {"username": "owner1", "email": "owner1@foodapp.com", "password": "owner123", "role": "owner"},
            {"username": "owner2", "email": "owner2@foodapp.com", "password": "owner123", "role": "owner"},
            {"username": "staff1", "email": "staff1@foodapp.com", "password": "staff123", "role": "staff"},
            {"username": "staff2", "email": "staff2@foodapp.com", "password": "staff123", "role": "staff"},
        ]
        
        for user_info in user_data:
            user = User(
                username=user_info["username"],
                email=user_info["email"],
                role=user_info["role"]
            )
            user.set_password(user_info["password"])
            db.session.add(user)
            users.append(user)
        
        # Create customers
        print("Creating customers...")
        customers = []
        customer_names = ["Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D", "Hoàng Văn E"]
        for i, name in enumerate(customer_names):
            customer = Customer(
                user=users[0],  # Use admin user for customers
                full_name=name,
                phone=f"090123456{i}",
                address=f"Địa chỉ {i+1}, TP.HCM",
                latitude=10.754792 + random.uniform(-0.01, 0.01),
                longitude=106.6952276 + random.uniform(-0.01, 0.01)
            )
            db.session.add(customer)
            customers.append(customer)
        
        print("Creating restaurants...")
        restaurants = []
        restaurant_names = [
            "Phở Cô Ba", "Hủ Tiếu Mỹ Tho", "Bún Bò Huế", "Cơm Tấm Sài Gòn",
            "Bánh Mì Hoà Bình", "Phở Ông Sáu", "Hủ Tiếu Cô Bảy", "Bún Thịt Nướng Cô Tám",
            "Cơm Tấm Ông Chín", "Bánh Xèo Cô Mười", "Phở Cô Một", "Hủ Tiếu Ông Hai",
            "Bún Bò Cô Ba", "Cơm Tấm Ông Tư", "Bánh Mì Cô Năm", "Phở Ông Sáu",
            "Hủ Tiếu Cô Bảy", "Bún Thịt Nướng Ông Tám", "Cơm Tấm Cô Chín", "Bánh Xèo Ông Mười"
        ]
        
        # Restaurant specialties (2-4 dishes per restaurant)
        restaurant_specialties = [
            ["Phở", "Bánh mì"],  # Phở Cô Ba
            ["Hủ tiếu", "Bánh cuốn"],  # Hủ Tiếu Mỹ Tho
            ["Bún bò", "Nem chua"],  # Bún Bò Huế
            ["Cơm tấm", "Bánh xèo"],  # Cơm Tấm Sài Gòn
            ["Bánh mì", "Bánh bèo"],  # Bánh Mì Hoà Bình
            ["Phở", "Bánh bột lọc"],  # Phở Ông Sáu
            ["Hủ tiếu", "Bánh canh"],  # Hủ Tiếu Cô Bảy
            ["Bún thịt nướng", "Bánh cuốn"],  # Bún Thịt Nướng Cô Tám
            ["Cơm tấm", "Bánh mì"],  # Cơm Tấm Ông Chín
            ["Bánh xèo", "Bánh bèo"],  # Bánh Xèo Cô Mười
            ["Phở", "Bánh bột lọc"],  # Phở Cô Một
            ["Hủ tiếu", "Bánh canh"],  # Hủ Tiếu Ông Hai
            ["Bún bò", "Nem chua"],  # Bún Bò Cô Ba
            ["Cơm tấm", "Bánh xèo"],  # Cơm Tấm Ông Tư
            ["Bánh mì", "Bánh bèo"],  # Bánh Mì Cô Năm
            ["Phở", "Bánh bột lọc"],  # Phở Ông Sáu
            ["Hủ tiếu", "Bánh canh"],  # Hủ Tiếu Cô Bảy
            ["Bún thịt nướng", "Bánh cuốn"],  # Bún Thịt Nướng Ông Tám
            ["Cơm tấm", "Bánh mì"],  # Cơm Tấm Cô Chín
            ["Bánh xèo", "Bánh bèo"]   # Bánh Xèo Ông Mười
        ]
        
        for i, (name, specialties) in enumerate(zip(restaurant_names, restaurant_specialties)):
            # Random coordinates in HCMC area
            lat = random.uniform(10.736261, 10.883040)
            lon = random.uniform(106.618361, 106.798821)
            
            restaurant = Restaurant(
                name=name,
                address=f"Địa chỉ {i+1}, Quận {random.randint(1, 12)}, TP.HCM",
                phone=f"090123456{i:02d}",
                email=f"restaurant{i+1}@foodapp.com",
                description=f"Quán {name} chuyên về {', '.join(specialties)}",
                image_url=random.choice([
                    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
                    "https://images.unsplash.com/photo-1552566626-52f8b828add9",
                    "https://images.unsplash.com/photo-1559339352-11d035aa65de"
                ]),
                is_active=True,
                opening_hours="07:00-22:00",
                owner=users[1] if i % 2 == 0 else users[2],  # Alternate between owners
                latitude=lat,
                longitude=lon,
                tax_code=f"0123456789{i:02d}",
                approval_status="approved",
                approval_date=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(restaurant)
            restaurants.append(restaurant)
        
        db.session.commit()
        
        print("Creating toppings...")
        toppings = []
        topping_data = [
            {"name": "Tôm khô", "price": 5000},
            {"name": "Mỡ hành", "price": 3000},
            {"name": "Chả lụa", "price": 7000},
            {"name": "Nước mắm", "price": 2000},
            {"name": "Thêm thịt", "price": 10000},
            {"name": "Thêm rau sống", "price": 5000},
            {"name": "Thêm nước chấm", "price": 2000},
            {"name": "Thêm tôm", "price": 15000},
            {"name": "Thêm mực", "price": 20000},
            {"name": "Thêm trứng cút", "price": 8000},
            {"name": "Thêm bánh canh", "price": 10000},
            {"name": "Thêm chả cá", "price": 12000},
            {"name": "Thêm sườn", "price": 15000},
            {"name": "Thêm chả trứng", "price": 10000},
            {"name": "Rau thơm", "price": 5000}
        ]
        
        for topping_info in topping_data:
            topping = Topping(
                name=topping_info["name"],
                price=topping_info["price"]
            )
            db.session.add(topping)
            toppings.append(topping)
        
        print("Creating foods...")
        foods = []
        
        # Map food names to their data
        food_map = {food["name"]: food for food in food_data}
        
        for i, (restaurant, specialties) in enumerate(zip(restaurants, restaurant_specialties)):
            for specialty in specialties:
                if specialty in food_map:
                    food_info = food_map[specialty]
                    
                    # Create food with restaurant-specific name
                    food_name = f"{specialty} {restaurant.name}"
                    price = random.choice(food_info["random_price"])
                    
                    food = Food(
                        name=food_name,
                        description=food_info["description"],
                        price=price,
                        image_url=random.choice(food_info["images"]),
                        is_available=True,
                        restaurant=restaurant,
                        preparation_time=random.randint(10, 30)
                    )
                    db.session.add(food)
                    foods.append(food)
                    
                    # Add categories
                    for cat_id in food_info["categories"]:
                        if cat_id in categories:
                            food.categories.append(categories[cat_id])
                    
                    # Add toppings
                    for topping_info in food_info["topping"]:
                        # Find matching topping or create new one
                        matching_topping = None
                        for topping in toppings:
                            if topping.name == topping_info["name"]:
                                matching_topping = topping
                                break
                        
                        if matching_topping:
                            food.toppings.append(matching_topping)
        
        print("Creating coupons...")
        coupons = []
        for i in range(10):
            coupon = Coupon(
                code=f"DISCOUNT{i+1:02d}",
                description=f"Mã giảm giá {i+1}",
                discount_type="percentage" if i % 2 == 0 else "fixed",
                discount_value=10 if i % 2 == 0 else 5000,
                min_order_amount=50000,
                max_discount=20000,
                usage_limit=100,
                used_count=random.randint(0, 50),
                start_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                end_date=datetime.now() + timedelta(days=random.randint(30, 90)),
                is_active=True,
                restaurant=random.choice(restaurants) if i % 3 == 0 else None
            )
            db.session.add(coupon)
            coupons.append(coupon)
        
        print("Creating orders...")
        orders = []
        for i in range(50):
            customer = random.choice(customers)
            restaurant = random.choice(restaurants)
            order_status = random.choice(["pending", "confirmed", "preparing", "ready", "delivered", "cancelled"])
            
            order = Order(
                customer=customer,
                restaurant=restaurant,
                total_amount=Decimal(str(random.randint(50000, 200000))),
                status=order_status,
                delivery_address=customer.address,
                delivery_phone=customer.phone,
                notes=f"Ghi chú đơn hàng {i+1}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
            )
            
            if order_status == "cancelled":
                order.cancel_reason = random.choice(cancel_reasons)
                order.cancel_note = f"Lý do hủy đơn hàng {i+1}"
            
            db.session.add(order)
            orders.append(order)
            
            # Add order items
            restaurant_foods = [f for f in foods if f.restaurant == restaurant]
            if restaurant_foods:
                num_items = random.randint(1, 3)
                selected_foods = random.sample(restaurant_foods, min(num_items, len(restaurant_foods)))
                
                for food in selected_foods:
                    quantity = random.randint(1, 3)
                    item = OrderItem(
                        order=order,
                        food=food,
                        quantity=quantity,
                        unit_price=food.price,
                        total_price=food.price * quantity
                    )
                    db.session.add(item)
                    
                    # Add toppings to some items
                    if food.toppings and random.random() < 0.3:
                        selected_toppings = random.sample(food.toppings, min(2, len(food.toppings)))
                        for topping in selected_toppings:
                            item.toppings.append(topping)
        
        print("Creating reviews...")
        for i in range(30):
            order = random.choice(orders)
            if order.status == "delivered":
                review = Review(
                    order=order,
                    customer=order.customer,
                    restaurant=order.restaurant,
                    rating=random.randint(3, 5),
                    comment=f"Đánh giá món ăn {i+1}",
                    created_at=order.created_at + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(review)
        
        print("Creating invoices...")
        for order in orders:
            if order.status in ["delivered", "ready"]:
                invoice = Invoice(
                    order=order,
                    subtotal=order.total_amount,
                    tax_amount=Decimal(str(float(order.total_amount) * 0.1)),  # 10% tax
                    total_amount=order.total_amount + Decimal(str(float(order.total_amount) * 0.1)),
                    payment_method=random.choice(["cash", "card", "momo", "zalo"]),
                    payment_status="paid",
                    third_party_code=f"PAY{order.id:06d}",
                    third_party_name=random.choice(["MoMo", "ZaloPay", "VNPay", "Cash"]),
                    created_at=order.created_at + timedelta(minutes=random.randint(5, 30))
                )
                db.session.add(invoice)
        
        print("Creating carts...")
        for customer in customers:
            if random.random() < 0.3:  # 30% chance to have cart
                cart = Cart(customer=customer)
                db.session.add(cart)
                
                # Add cart items
                num_items = random.randint(1, 3)
                selected_foods = random.sample(foods, num_items)
                
                for food in selected_foods:
                    cart_item = CartItem(
                        cart=cart,
                        food=food,
                        quantity=random.randint(1, 2)
                    )
                    db.session.add(cart_item)
                    
                    # Add toppings to some items
                    if food.toppings and random.random() < 0.2:
                        selected_toppings = random.sample(food.toppings, min(1, len(food.toppings)))
                        for topping in selected_toppings:
                            cart_item.toppings.append(topping)
        
        db.session.commit()
        print("Sample data created successfully!")

if __name__ == "__main__":
    create_sample_data()