import unittest
from app import app, db
from models import User, Skateboard
import json

class TestAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            self.create_test_data()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_data(self):
        Skateboard.query.delete()
        db.session.commit()
        skateboards = [
            Skateboard(
                name="Test Board 1",
                brand="Element",
                price=4999.99,
                description="Test description 1",
                image_url="http://example.com/board1.jpg",
                stock=10
            ),
            Skateboard(
                name="Test Board 2",
                brand="Santa Cruz",
                price=5999.99,
                description="Test description 2",
                image_url="http://example.com/board2.jpg",
                stock=5
            )
        ]
        db.session.add_all(skateboards)
        db.session.commit()

    def test_get_all_skateboards(self):
        """Тест получения списка всех скейтбордов"""
        response = self.client.get('/api/skateboards')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['brand'], 'Element')
        self.assertEqual(data[1]['brand'], 'Santa Cruz')

    def test_get_skateboards_with_filters(self):
        """Тест фильтрации скейтбордов"""
        # Тест фильтра по цене
        response = self.client.get('/api/skateboards?min_price=5000&max_price=6000')
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['brand'], 'Santa Cruz')

        # Тест фильтра по бренду
        response = self.client.get('/api/skateboards?brand=Element')
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['brand'], 'Element')

        # Тест фильтра по наличию
        response = self.client.get('/api/skateboards?in_stock=true')
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    def test_get_skateboards_sorting(self):
        """Тест сортировки скейтбордов"""
        # Сортировка по возрастанию цены
        response = self.client.get('/api/skateboards?sort_order=asc')
        data = json.loads(response.data)
        self.assertEqual(data[0]['price'], 4999.99)
        self.assertEqual(data[1]['price'], 5999.99)

        # Сортировка по убыванию цены
        response = self.client.get('/api/skateboards?sort_order=desc')
        data = json.loads(response.data)
        self.assertEqual(data[0]['price'], 5999.99)
        self.assertEqual(data[1]['price'], 4999.99)

    def test_get_single_skateboard(self):
        response = self.client.get('/api/skateboards/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['brand'], 'Element')
        self.assertEqual(data['price'], 4999.99)

    def test_get_nonexistent_skateboard(self):
        response = self.client.get('/api/skateboards/999')
        self.assertEqual(response.status_code, 404)

    def test_invalid_price_filter(self):
        response = self.client.get('/api/skateboards?min_price=invalid')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

if __name__ == '__main__':
    unittest.main()
