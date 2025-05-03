from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin
        }


class Skateboard(db.Model):
    __tablename__ = 'skateboards'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'price': self.price,
            'description': self.description,
            'image_url': self.image_url,
            'stock': self.stock,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def get_sample_skateboards():
        return [
            Skateboard(
                name='Pro Model Complete',
                brand='Element',
                price=89.99,
                description='Профессиональный скейтборд с высококачественными компонентами',
                image_url='https://example.com/element-pro.jpg',
                stock=10
            ),
            Skateboard(
                name='Street Cruiser',
                brand='Santa Cruz',
                price=79.99,
                description='Идеально подходит для уличного катания и круизинга',
                image_url='https://example.com/santa-cruz-cruiser.jpg',
                stock=15
            ),
            Skateboard(
                name='Beginner Board',
                brand='Powell Peralta',
                price=69.99,
                description='Отличный выбор для начинающих с плавной ездой и стабильностью',
                image_url='https://example.com/powell-beginner.jpg',
                stock=20
            )
        ]
