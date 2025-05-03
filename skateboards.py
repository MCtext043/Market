from models import Skateboard, db


def get_all_skateboards():
    return Skateboard.query.all()


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
