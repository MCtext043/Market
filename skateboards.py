from models import Skateboard, db
from sqlalchemy import desc, asc


def get_all_skateboards(filters=None, sort_by=None, sort_order='asc'):
    query = Skateboard.query
    if filters:
        if 'min_price' in filters:
            query = query.filter(Skateboard.price >= filters['min_price'])
        if 'max_price' in filters:
            query = query.filter(Skateboard.price <= filters['max_price'])
        if 'brand' in filters:
            query = query.filter(Skateboard.brand == filters['brand'])
        if 'in_stock' in filters and filters['in_stock']:
            query = query.filter(Skateboard.stock > 0)
    if sort_by == 'price':
        sort_column = Skateboard.price
    else:
        sort_column = Skateboard.price
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    return query.all()


def get_skateboard_by_id(skateboard_id):
    return Skateboard.query.get_or_404(skateboard_id)


def create_skateboard(name, brand, price, description, image_url, stock):
    skateboard = Skateboard(
        name=name,
        brand=brand,
        price=price,
        description=description,
        image_url=image_url,
        stock=stock
    )
    db.session.add(skateboard)
    db.session.commit()
    return skateboard


def update_skateboard(skateboard_id, **kwargs):
    skateboard = get_skateboard_by_id(skateboard_id)
    for key, value in kwargs.items():
        if hasattr(skateboard, key):
            setattr(skateboard, key, value)
    db.session.commit()
    return skateboard


def delete_skateboard(skateboard_id):
    skateboard = get_skateboard_by_id(skateboard_id)
    db.session.delete(skateboard)
    db.session.commit()
    return True


def search_skateboards(query):
    return Skateboard.query.filter(
        (Skateboard.name.ilike(f'%{query}%')) |
        (Skateboard.brand.ilike(f'%{query}%')) |
        (Skateboard.description.ilike(f'%{query}%'))
    ).all()


def get_skateboards_by_brand(brand):
    return Skateboard.query.filter_by(brand=brand).all()


def get_skateboards_by_price_range(min_price, max_price):
    return Skateboard.query.filter(
        Skateboard.price >= min_price,
        Skateboard.price <= max_price
    ).all()


def get_skateboards_in_stock():
    return Skateboard.query.filter(Skateboard.stock > 0).all()


def update_stock(skateboard_id, quantity):
    skateboard = get_skateboard_by_id(skateboard_id)
    skateboard.stock += quantity
    db.session.commit()
    return skateboard


def get_all_brands():
    return db.session.query(Skateboard.brand).distinct().all()
