from food_app import create_app, db
from food_app.models.user import User
from food_app.models.customer import Customer
from food_app.models.restaurant import Restaurant
from food_app.models.food import Food
from food_app.models.category import Category
from food_app.models.otp import OTP
from datetime import datetime

app = create_app()

def init_sample_data():
    with app.app_context():
        # Tạo bảng
        db.create_all()
        print("Đã tạo các bảng database...")

        # 1. Tạo owner trước (user với role 'owner')
        if User.query.filter_by(username='restaurant_owner').first() is None:
            owner = User(
                first_name='Nguyễn Văn',
                last_name='Chủ',
                username='restaurant_owner',
                phone='0123456788',
                email='owner@restaurant.com',
                gender='male',
                role='owner',  # Role mới
                user_type='staff'
                # KHÔNG gán restaurant_id cho owner
            )
            owner.set_password('owner123')
            db.session.add(owner)
            db.session.commit()
            print("✓ Đã tạo tài khoản owner")
        else:
            owner = User.query.filter_by(username='restaurant_owner').first()

        # 2. Tạo nhà hàng cho owner (duy nhất 1)
        if not owner.owned_restaurant:
            restaurant = Restaurant(
                name='Quán Cơm Tấm Sài Gòn',
                address='123 Nguyễn Văn Cừ, Q.5, TP.HCM',
                phone='0283456789',
                email='contact@comtam.com',
                description='Quán cơm tấm truyền thống Sài Gòn',
                owner_id=owner.id,  # Gán owner
                tax_code='1234567890',  # Bổ sung mã số thuế
                approval_status='approved',  # Đã phê duyệt
                opening_hours={
                    'mon': '6:00-22:00',
                    'tue': '6:00-22:00',
                    'wed': '6:00-22:00',
                    'thu': '6:00-22:00',
                    'fri': '6:00-22:00',
                    'sat': '6:00-23:00',
                    'sun': '6:00-23:00'
                }
            )
            db.session.add(restaurant)
            db.session.commit()
            print("✓ Đã tạo nhà hàng cho owner")
        else:
            restaurant = owner.owned_restaurant

        # 3. Tạo admin (không cần restaurant_id)
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
                # Admin không thuộc restaurant nào
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Đã tạo tài khoản admin")

        # 4. Tạo manager và gán vào restaurant qua invitation
        if User.query.filter_by(username='manager').first() is None:
            manager = User(
                first_name='Nguyễn Văn',
                last_name='Quản Lý',
                username='manager',
                phone='0123456790',
                email='manager@restaurant.com',
                gender='male',
                role='manager',
                restaurant_id=restaurant.id,  # Gán trực tiếp cho demo
                user_type='staff'
            )
            manager.set_password('manager123')
            db.session.add(manager)
            print("✓ Đã tạo tài khoản manager")

        # 5. Tạo staff và gán vào restaurant qua invitation
        if User.query.filter_by(username='staff').first() is None:
            staff = User(
                first_name='Trần Thị',
                last_name='Nhân Viên',
                username='staff',
                phone='0123456791',
                email='staff@restaurant.com',
                gender='female',
                role='staff',
                restaurant_id=restaurant.id,  # Gán trực tiếp cho demo
                user_type='staff'
            )
            staff.set_password('staff123')
            db.session.add(staff)
            print("✓ Đã tạo tài khoản staff")

        # 6. Tạo customer mẫu (sử dụng số điện thoại linh động)
        if Customer.query.filter_by(phone='0987654321').first() is None:
            customer = Customer(
                first_name='Lê Văn',
                last_name='Khách',
                phone='0987654321',  # Số điện thoại hợp lệ
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
                phone='0987654322',  # Số điện thoại hợp lệ
                email='customer@example.com',
                gender='female',
                address='789 Nguyễn Huệ, Q.1, TP.HCM',
                user_type='customer'
            )
            db.session.add(customer2)
            print("✓ Đã tạo customer 2")

        # 7. Thêm món ăn
        if Food.query.count() == 0:
            # Tạo các category trước
            category_comtam = Category.query.filter_by(name='Cơm Tấm').first()
            category_dacsan = Category.query.filter_by(name='Đặc Sản').first()
            category_douong = Category.query.filter_by(name='Đồ Uống').first()

            foods_data = [
                {
                    'name': 'Cơm Tấm Sườn Nướng',
                    'description': 'Cơm tấm sườn nướng truyền thống',
                    'price': 45000,
                    'restaurant_id': restaurant.id,
                    'categories': [category_comtam] if category_comtam else []
                },
                {
                    'name': 'Cơm Tấm Bì Chả',
                    'description': 'Cơm tấm bì chả thơm ngon',
                    'price': 40000,
                    'restaurant_id': restaurant.id,
                    'categories': [category_comtam] if category_comtam else []
                },
                {
                    'name': 'Cơm Tấm Đặc Biệt',
                    'description': 'Cơm tấm sườn bì chả trứng',
                    'price': 55000,
                    'restaurant_id': restaurant.id,
                    'categories': [category_comtam] if category_comtam else []
                },
                {
                    'name': 'Chả Cá Thăng Long',
                    'description': 'Chả cá Hà Nội đặc biệt',
                    'price': 65000,
                    'restaurant_id': restaurant.id,
                    'categories': [category_dacsan] if category_dacsan else []
                },
                {
                    'name': 'Nước Mía',
                    'description': 'Nước mía tươi mát',
                    'price': 15000,
                    'restaurant_id': restaurant.id,
                    'categories': [category_douong] if category_douong else []
                }
            ]
            
            for food_data in foods_data:
                categories = food_data.pop('categories', [])
                food = Food(**food_data)
                food.categories.extend(categories)
                db.session.add(food)
            
            db.session.commit()
            print("✓ Đã tạo món ăn mẫu")

        # Tạo các category nếu chưa có
        categories_to_create = [
            {'name': 'Cơm Tấm', 'description': 'Các món cơm tấm truyền thống'},
            {'name': 'Đặc Sản', 'description': 'Các món đặc sản'},
            {'name': 'Đồ Uống', 'description': 'Các loại đồ uống'}
        ]
        for cat in categories_to_create:
            if not Category.query.filter_by(name=cat['name']).first():
                db.session.add(Category(**cat))
        db.session.commit()

        # Lấy lại các category (sau khi chắc chắn đã có)
        category_comtam = Category.query.filter_by(name='Cơm Tấm').first()
        category_dacsan = Category.query.filter_by(name='Đặc Sản').first()
        category_douong = Category.query.filter_by(name='Đồ Uống').first()

        db.session.commit()
        print('\n🎉 Đã khởi tạo dữ liệu mẫu thành công!')
        print('\n📋 Tài khoản mẫu:')
        print('- Owner: owner@restaurant.com / owner123')
        print('- Admin: admin@foodapp.com / admin123')
        print('- Manager: manager@restaurant.com / manager123')  
        print('- Staff: staff@restaurant.com / staff123')
        print('- Customer: Sử dụng OTP với số điện thoại 0987654321 hoặc 0987654322')

if __name__ == '__main__':
    init_sample_data()