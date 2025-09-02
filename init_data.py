from food_app import create_app, db
from food_app.models.user import User
from food_app.models.customer import Customer
from food_app.models.restaurant import Restaurant
from food_app.models.food import Food
from food_app.models.category import Category
from datetime import datetime
import random

app = create_app()

def init_sample_data():
    with app.app_context():
        db.create_all()
        print("Đã tạo lại schema database...")

        # Admin account
        if User.query.filter_by(username='admin').first() is None:
            admin = User(
                first_name='Quản trị',
                last_name='Viên',
                username='admin',
                phone='0123456789',
                email='admin@foodapp.com',
                gender='male',
                role='admin',
                user_type='staff'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Đã tạo tài khoản admin")
        # Customers
        if Customer.query.filter_by(phone='0987654321').first() is None:
            customer = Customer(
                first_name='Lê Văn',
                last_name='Khách',
                phone='0987654321',  
                gender='male',
                address='456 Lê Văn Sỹ, Q.3, TP.HCM',
                user_type='customer'
            )
            db.session.add(customer)
            print("✓ Đã tạo customer 1")

        if Customer.query.filter_by(phone='0987654322').first() is None:
            customer2 = Customer(
                first_name='Nguyễn Thị',
                last_name='Hoa',
                phone='0987654322',  
                email='customer@example.com',
                gender='female',
                address='789 Nguyễn Huệ, Q.1, TP.HCM',
                user_type='customer'
            )
            db.session.add(customer2)
            print("✓ Đã tạo customer 2")

        # Categories
        categories_to_create = [
            {'name': 'Cơm Tấm', 'description': 'Các món cơm tấm truyền thống'},
            {'name': 'Đặc Sản', 'description': 'Các món đặc sản'},
            {'name': 'Đồ Uống', 'description': 'Các loại đồ uống'},
            {'name': 'Phở', 'description': 'Các món phở'},
            {'name': 'Bún', 'description': 'Các món bún'},
        ]
        for cat in categories_to_create:
            db.session.merge(Category(**cat))
        db.session.commit()

        categories = {c.name: c for c in Category.query.all()}

        # Generate > 20 restaurants around HCMC center with random coords
        center_lat, center_lon = 10.776889, 106.700806
        def jitter(max_km=15):
            # ~1 deg lat = 111km
            dlat = random.uniform(-max_km, max_km) / 111.0
            import math
            dlon = random.uniform(-max_km, max_km) / (111.0 * max(math.cos(math.radians(center_lat)), 0.01))
            return dlat, dlon

        vietnam_food_names = [
            'Cơm Tấm Sườn', 'Cơm Tấm Bì Chả', 'Cơm Gà Xối Mỡ', 'Phở Bò', 'Phở Gà',
            'Bún Bò Huế', 'Bún Chả Cá', 'Bún Thịt Nướng', 'Hủ Tiếu Nam Vang', 'Bánh Mì Thịt',
            'Bánh Xèo', 'Bánh Cuốn', 'Gỏi Cuốn', 'Miến Gà', 'Cháo Sườn'
        ]

        num_restaurants = 22
        for i in range(num_restaurants):
            owner = User(
                first_name='Owner', last_name=str(i+1), username=f'owner{i+1}',
                phone=f'090000{i:03d}', email=f'owner{i+1}@demo.com', gender='male', role='owner', user_type='staff'
            )
            owner.set_password('owner123')
            db.session.add(owner)
            db.session.flush()

            dlat, dlon = jitter()
            lat = center_lat + dlat
            lon = center_lon + dlon
            rest = Restaurant(
                name=f'Nhà hàng {i+1}',
                address=f'{100+i} Đường Demo, Q.{(i%12)+1}, TP.HCM',
                phone=f'0283{i:07d}',
                email=f'rest{i+1}@demo.com',
                description='Nhà hàng Việt Nam',
                owner_id=owner.id,
                tax_code=f'{1000000000+i}',
                approval_status='approved',
                opening_hours={'mon':'7:00-22:00','tue':'7:00-22:00','wed':'7:00-22:00','thu':'7:00-22:00','fri':'7:00-22:00','sat':'7:00-23:00','sun':'7:00-23:00'},
                latitude=lat,
                longitude=lon
            )
            db.session.add(rest)
            db.session.flush()

            # 5 foods per restaurant
            for j in range(5):
                name = random.choice(vietnam_food_names)
                price = random.choice([30000, 35000, 40000, 45000, 50000, 60000])
                food = Food(
                    name=f'{name} #{j+1}',
                    description=f'{name} hương vị Việt',
                    price=price,
                    restaurant_id=rest.id,
                    available=True
                )
                db.session.add(food)

        db.session.commit()
        print(f"✓ Đã tạo {num_restaurants} nhà hàng, mỗi nhà hàng 5 món ăn")

        print('\n🎉 Khởi tạo dữ liệu mẫu hoàn tất!')

if __name__ == '__main__':
    init_sample_data()