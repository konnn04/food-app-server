from app import create_app, db
from app.models.user import User
from app.models.customer import Customer
from app.models.restaurant import Restaurant
from app.models.food import Food

app = create_app()

def init_sample_data():
    with app.app_context():
        # Tạo bảng
        db.create_all()
        
        # Tạo nhà hàng mẫu
        if Restaurant.query.count() == 0:
            restaurant = Restaurant(
                name='Quán Cơm Tấm Sài Gòn',
                address='123 Nguyễn Văn Cừ, Q.5, TP.HCM',
                phone='0283456789',
                email='contact@comtam.com',
                description='Quán cơm tấm truyền thống Sài Gòn',
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
        
        restaurant = Restaurant.query.first()
        
        # Tạo admin
        if User.query.filter_by(username='admin').first() is None:
            admin = User(
                username='admin',
                phone='0123456789',
                email='admin@foodapp.com',
                full_name='Quản trị viên',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Tạo manager
        if User.query.filter_by(username='manager').first() is None:
            manager = User(
                username='manager',
                phone='0123456790',
                email='manager@restaurant.com',
                full_name='Nguyễn Văn Quản Lý',
                role='manager',
                restaurant_id=restaurant.id
            )
            manager.set_password('manager123')
            db.session.add(manager)
        
        # Tạo staff
        if User.query.filter_by(username='staff').first() is None:
            staff = User(
                username='staff',
                phone='0123456791',
                email='staff@restaurant.com',
                full_name='Trần Thị Nhân Viên',
                role='staff',
                restaurant_id=restaurant.id
            )
            staff.set_password('staff123')
            db.session.add(staff)
        
        # Tạo customer mẫu
        if Customer.query.filter_by(phone='0987654321').first() is None:
            customer = Customer(
                phone='0987654321',
                full_name='Lê Văn Khách',
                address='456 Lê Văn Sỹ, Q.3, TP.HCM',
                gender='male'
            )
            db.session.add(customer)

        # Tạo thêm customer
        if Customer.query.filter_by(phone='0987654322').first() is None:
            customer2 = Customer(
                phone='0987654322',
                full_name='Nguyễn Thị Hoa',
                address='789 Nguyễn Huệ, Q.1, TP.HCM',
                gender='female',
                email='customer@example.com'
            )
            db.session.add(customer2)

        # Thêm món ăn
        if Food.query.count() == 0:
            foods = [
                Food(name='Cơm Tấm Sườn Nướng', description='Cơm tấm sườn nướng truyền thống', 
                     price=45000, category='Cơm Tấm', restaurant_id=restaurant.id),
                Food(name='Cơm Tấm Bì Chả', description='Cơm tấm bì chả thơm ngon', 
                     price=40000, category='Cơm Tấm', restaurant_id=restaurant.id),
                Food(name='Cơm Tấm Đặc Biệt', description='Cơm tấm sườn bì chả trứng', 
                     price=55000, category='Cơm Tấm', restaurant_id=restaurant.id),
                Food(name='Chả Cá Thăng Long', description='Chả cá Hà Nội đặc biệt', 
                     price=65000, category='Đặc Sản', restaurant_id=restaurant.id),
                Food(name='Nước Mía', description='Nước mía tươi mát', 
                     price=15000, category='Đồ Uống', restaurant_id=restaurant.id),
            ]
            
            for food in foods:
                db.session.add(food)
        
        db.session.commit()
        print('Đã khởi tạo dữ liệu mẫu thành công!')
        print('Tài khoản mẫu:')
        print('- Admin: admin@foodapp.com / admin123')
        print('- Manager: manager@restaurant.com / manager123')  
        print('- Staff: staff@restaurant.com / staff123')
        print('- Customer: Sử dụng OTP với số điện thoại 0987654321 hoặc 0987654322')

if __name__ == '__main__':
    init_sample_data()