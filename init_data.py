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
            {"code": "CUSTOMER_CANCEL", "description": "Khách hàng yêu cầu hủy"},
            {"code": "RESTAURANT_UNAVAILABLE", "description": "Nhà hàng không thể phục vụ"},
            {"code": "DELIVERY_TIMEOUT", "description": "Thời gian giao hàng quá lâu"},
            {"code": "OUT_OF_STOCK", "description": "Sản phẩm hết hàng"},
            {"code": "OTHER", "description": "Lý do khác"}
        ]
        for reason in reasons:
            cancel_reason = CancelReason(**reason)
            db.session.add(cancel_reason)
            cancel_reasons.append(cancel_reason)
        
        print("Creating users...")
        users = []
        user_data = [
            {"username": "admin", "email": "admin@foodapp.com", "password": "admin123", "role": "admin"},
        ]
        
        # Create owners (165 owners cho 165 restaurants)
        for i in range(165):
            user_data.append({
                "username": f"owner{i+1}", 
                "email": f"owner{i+1}@foodapp.com", 
                "password": "owner123", 
                "role": "owner"
            })
        
        # No extra staff accounts in owner-only model
        
        for user_info in user_data:
            user = User(
                username=user_info["username"],
                email=user_info["email"],
                role=user_info["role"]
            )
            user.set_password(user_info["password"])
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        
        # Create customers
        print("Creating customers...")
        customers = []
        customer_names = [
            ("Nguyễn", "Văn A"), ("Trần", "Thị B"), ("Lê", "Văn C"), 
            ("Phạm", "Thị D"), ("Hoàng", "Văn E")
        ]
        for i, (first_name, last_name) in enumerate(customer_names):
            customer = Customer(
                first_name=first_name,
                last_name=last_name,
                phone=f"090123456{i}",
                address=f"Địa chỉ {i+1}, TP.HCM",
                email=f"customer{i+1}@foodapp.com"
            )
            db.session.add(customer)
            customers.append(customer)
        
        print("Creating restaurants...")
        restaurants = []
        
        # Tạo 3 mảng để kết hợp thành tên nhà hàng
        xung_ho = ["Bác", "Cô", "Chú", "Ông", "Bà", "Chị"]
        thu_tu = ["Moggu", "Qiqi", "Tều", "Sleo", "Anh", "Sleo", "Taku", "Quagmire", "Giffin", "Tèo", "Mèo"]
        co_so = ["Nhà làm", "Cơ sở 1", "Cơ sở 2", "Cơ sở 3", "Cơ sở 4", "Cơ sở 5", "Cơ sở 6", "Cơ sở 7", "Cơ sở 8", "Cơ sở 9", "Cơ sở 10"]
        
        # Tạo danh sách tên nhà hàng bằng cách kết hợp
        restaurant_names = []
        for xh in xung_ho:
            for tt in thu_tu:
                for cs in co_so:
                    restaurant_names.append(f"{xh} {tt} {cs}")
        
        # Đảm bảo có đủ 165 nhà hàng
        if len(restaurant_names) < 165:
            # Thêm các tên khác nếu cần
            additional_names = [
                "Quán ăn Cô Ba", "Lò nem chua Hoa Thánh", "Bánh mì Mèo Sáu", 
                "Phở Cô Một", "Hủ tiếu Cô Bảy", "Bún bò Cô Ba",
                "Cơm tấm Chú Chín", "Bánh xèo Cô Mười", "Bánh bèo Cô Tám",
                "Bánh cuốn Cô Năm", "Bánh bột lọc Cô Sáu", "Bánh canh Cô Bảy",
                "Bún thịt nướng Cô Tám", "Nem chua Chú Chín", "Bánh mì Cô Mười"
            ]
            restaurant_names.extend(additional_names)
        
        # Giới hạn đúng 165 nhà hàng
        restaurant_names = restaurant_names[:165]
        
        # Định nghĩa chuyên môn cho từng nhà hàng (mỗi loại món được bán bởi nhiều nhà hàng)
        restaurant_specialties = []
        
        # Bánh bèo (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Bánh bèo"])
        
        # Nem chua (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Nem chua"])
        
        # Bánh mì (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Bánh mì"])
        
        # Phở (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Phở"])
        
        # Hủ tiếu (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Hủ tiếu"])
        
        # Bún bò (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Bún bò"])
        
        # Cơm tấm (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Cơm tấm"])
        
        # Bánh xèo (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Bánh xèo"])
        
        # Bánh cuốn (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Bánh cuốn"])
        
        # Bánh bột lọc (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Bánh bột lọc"])
        
        # Bánh canh (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Bánh canh"])
        
        # Bún thịt nướng (15 nhà hàng)
        for i in range(15):
            restaurant_specialties.append(["Bún thịt nướng"])
        
        for i, (name, specialties) in enumerate(zip(restaurant_names, restaurant_specialties)):
            # Random coordinates in HCMC area
            lat = random.uniform(10.736261, 10.883040)
            lon = random.uniform(106.618361, 106.798821)
            
            restaurant = Restaurant(
                name=f"{specialties[0]} {name}",
                address=f"Địa chỉ {i+1}, Quận {random.randint(1, 12)}, TP.HCM",
                phone=f"090123456{i:03d}",
                email=f"restaurant{i+1}@foodapp.com",
                description=f"{name} chuyên về {', '.join(specialties)}",
                image_url=random.choice([
                    "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
                    "https://images.unsplash.com/photo-1552566626-52f8b828add9",
                    "https://images.unsplash.com/photo-1559339352-11d035aa65de"
                ]),
                is_active=True,
                opening_hours="07:00-22:00",
                owner_id=users[i+1].id,  # i+1 because users[0] is admin 
                latitude=lat,
                longitude=lon,
                tax_code=f"0123456789{i:03d}",
                approval_status="approved",
                approval_date=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(restaurant)
            restaurants.append(restaurant)
            
            # Update owner's restaurant_id
            owner = users[i+1]
            owner.restaurant_id = restaurant.id
            db.session.add(owner)
            db.session.commit()
        
        print("Creating foods...")
        foods = []
        
        # Tạo mapping từ tên loại món sang data trong JSON
        food_type_mapping = {
            "Bánh bèo": 0,      # index trong food_data
            "Bánh bột lọc": 1,
            "Bánh canh": 2,
            "Bánh cuốn": 3,
            "Bánh mì": 4,
            "Bánh xèo": 5,
            "Bún thịt nướng": 6,
            "Cơm tấm": 7,
            "Hủ tiếu": 8,
            "Nem chua": 9,
            "Phở": 10
        }
        
        # Tạo tất cả toppings từ data_food.json
        print("Creating toppings from food data...")
        all_toppings = {}  # Dictionary để tránh duplicate toppings
        
        for food_info in food_data:
            for topping_info in food_info["topping"]:
                topping_name = topping_info["name"]
                if topping_name not in all_toppings:
                    topping = Topping(
                        name=topping_name,
                        price=topping_info["price"]
                    )
                    db.session.add(topping)
                    all_toppings[topping_name] = topping
        
        db.session.commit()

        for i, (restaurant, specialties) in enumerate(zip(restaurants, restaurant_specialties)):
            for specialty in specialties:
                if specialty in food_type_mapping:
                    food_index = food_type_mapping[specialty]
                    food_info = food_data[food_index]
                    
                    # Lấy 3-5 món ngẫu nhiên từ danh sách names
                    num_foods = random.randint(3, min(5, len(food_info["names"])))
                    selected_names = random.sample(food_info["names"], num_foods)
                    
                    for j, food_name in enumerate(selected_names):
                        price = random.choice(food_info["random_price"])
                        
                        food = Food(
                            name=food_name,
                            description=food_info["description"],
                            price=price,
                            image_url=random.choice(food_info["images"]),
                            available=True,
                            restaurant=restaurant
                        )
                        db.session.add(food)
                        foods.append(food)
                        
                        # Add categories
                        for cat_id in food_info["categories"]:
                            if cat_id in categories:
                                food.categories.append(categories[cat_id])
                        
                        # Add toppings từ food_info
                        for topping_info in food_info["topping"]:
                            topping_name = topping_info["name"]
                            if topping_name in all_toppings:
                                food.toppings.append(all_toppings[topping_name])
        
        # Ensure owners have restaurant_id set (1-1 owner)
        for idx, restaurant in enumerate(restaurants):
            owner_user = users[idx+1]  # users[0] is admin; then owners in order
            owner_user.restaurant_id = restaurant.id
            db.session.add(owner_user)
        db.session.commit()

        print("Creating coupons...")
        coupons = []
        for i in range(10):
            coupon = Coupon(
                code=f"DISCOUNT{i+1:02d}",
                description=f"Mã giảm giá {i+1}",
                discount_type="percent" if i % 2 == 0 else "amount",
                discount_value=10 if i % 2 == 0 else 5000,
                min_order_amount=50000,
                max_discount_amount=20000,
                start_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                end_date=datetime.now() + timedelta(days=random.randint(30, 90)),
                is_active=True,
                restaurant=random.choice(restaurants) if i % 3 == 0 else None
            )
            db.session.add(coupon)
            coupons.append(coupon)
        
        print("Creating reviews...")
        reviews = []
        review_contents = [
            "Món ăn rất ngon, sẽ quay lại lần sau!",
            "Chất lượng tuyệt vời, đáng đồng tiền bát gạo.",
            "Món ăn ngon, nhưng phục vụ hơi chậm.",
            "Đồ ăn tươi và ngon, giá cả hợp lý.",
            "Hương vị đặc trưng, rất đáng để thử.",
            "Phần ăn hơi nhỏ so với giá tiền.",
            "Đồ ăn ngon, nhân viên thân thiện.",
            "Hương vị đúng chuẩn, sẽ ghé lại.",
            "Chất lượng ổn, giá hơi cao.",
            "Rất ngon, đúng với mô tả.",
            "Đồ ăn tươi ngon, không gian thoải mái."
        ]

        # Chọn số lượng đánh giá muốn tạo
        num_reviews = 500  # Ví dụ: tạo 500 đánh giá

        # Tạo đánh giá ngẫu nhiên
        for _ in range(num_reviews):
            customer = random.choice(customers)
            food = random.choice(foods)
            rating = random.randint(3, 5)  # Đánh giá từ 3-5 sao
            content = random.choice(review_contents)
            
            # Ngày đánh giá trong khoảng 3 tháng gần đây
            review_date = datetime.now() - timedelta(days=random.randint(0, 90))
            
            review = Review(
                customer_id=customer.id,
                food_id=food.id,
                restaurant_id=food.restaurant_id,
                rating=rating,
                comment=content,
                created_at=review_date
            )
            db.session.add(review)
            reviews.append(review)

        # Tạo một số đánh giá chi tiết hơn cho các món nổi bật
        detailed_reviews = [
            "Món này là đặc sản của quán, tôi rất thích hương vị đặc trưng và cách chế biến. Nguyên liệu tươi ngon, nước sốt vừa miệng. Nhân viên phục vụ nhiệt tình, không gian quán đẹp và sạch sẽ. Mình sẽ quay lại nhiều lần nữa!",
            "Đây là lần thứ 3 mình đặt món này và chất lượng luôn ổn định. Hương vị đậm đà, đúng chuẩn. Điểm cộng cho phần thức ăn được trình bày đẹp mắt. Giá cả hợp lý so với chất lượng.",
            "Mình là khách quen của quán và đặc biệt thích món này. Vị umami đặc trưng, nguyên liệu tươi ngon. Nhân viên phục vụ nhanh nhẹn và thân thiện. Không gian quán thoáng đãng, sạch sẽ.",
            "Món này có hương vị độc đáo mà không nơi nào có được. Nguyên liệu chọn lọc kỹ càng, chế biến vừa miệng. Phần ăn hơi nhỏ nhưng xứng đáng với giá tiền. Sẽ quay lại!",
            "Đây là món ăn yêu thích của gia đình mình. Trẻ con rất thích và người lớn cũng vậy. Món ăn được chế biến cẩn thận, vị ngon đúng điệu. Nhà hàng sạch sẽ, nhân viên thân thiện."
        ]

        # Tạo 50 đánh giá chi tiết cho các món ăn ngẫu nhiên với rating 5 sao
        for _ in range(50):
            customer = random.choice(customers)
            food = random.choice(foods)
            content = random.choice(detailed_reviews)
            
            # Đánh giá chi tiết thường là 5 sao
            review = Review(
                customer_id=customer.id,
                food_id=food.id,
                restaurant_id=food.restaurant_id,
                rating=5,
                comment=content,
                created_at=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(review)
            reviews.append(review)

        print(f"Created {len(reviews)} reviews!")

        db.session.commit()
        print("Sample data created successfully!")

if __name__ == "__main__":
    create_sample_data()
