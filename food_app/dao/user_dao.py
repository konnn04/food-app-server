from food_app import db
from food_app.models.user import User
from datetime import datetime

class UserDAO:
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_user_by_phone(phone):
        return User.query.filter_by(phone=phone).first()

    @staticmethod
    def get_user_by_credentials(credential):
        return User.query.filter(
            (User.username == credential) | (User.email == credential)
        ).first()

    @staticmethod
    def get_users_by_role(role=None):
        if role:
            return User.query.filter_by(role=role).all()
        return User.query.all()

    @staticmethod
    def create_user(user_data):
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user, update_data):
        for key, value in update_data.items():
            setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def update_last_login(user):
        user.last_login = datetime.utcnow()
        db.session.commit()
