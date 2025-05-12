from models import db, CartItem, Skateboard


def add_to_cart(user_id, skateboard_id, quantity=1):
    skateboard = Skateboard.query.get_or_404(skateboard_id)
    if skateboard.stock < quantity:
        return False, 'Недостаточно товара на складе'
    cart_item = CartItem.query.filter_by(
        user_id=user_id,
        skateboard_id=skateboard_id
    ).first()

    if cart_item:
        if skateboard.stock < cart_item.quantity + quantity:
            return False, 'Недостаточно товара на складе'
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=user_id,
            skateboard_id=skateboard_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    skateboard.stock -= quantity
    db.session.commit()
    return True, 'Товар добавлен в корзину'


def remove_from_cart(user_id, skateboard_id):
    cart_item = CartItem.query.filter_by(
        user_id=user_id,
        skateboard_id=skateboard_id
    ).first_or_404()
    skateboard = Skateboard.query.get(skateboard_id)
    skateboard.stock += cart_item.quantity
    db.session.delete(cart_item)
    db.session.commit()
    return True, 'Товар удален из корзины'


def update_cart_item_quantity(user_id, skateboard_id, quantity):
    cart_item = CartItem.query.filter_by(
        user_id=user_id,
        skateboard_id=skateboard_id
    ).first_or_404()
    skateboard = Skateboard.query.get(skateboard_id)
    quantity_diff = quantity - cart_item.quantity
    if skateboard.stock < quantity_diff:
        return False, 'Недостаточно товара на складе'
    cart_item.quantity = quantity
    skateboard.stock -= quantity_diff
    db.session.commit()
    return True, 'Количество товара обновлено'


def get_cart_items(user_id):
    return CartItem.query.filter_by(user_id=user_id).all()


def get_cart_total(user_id):
    cart_items = get_cart_items(user_id)
    total = sum(item.skateboard.price * item.quantity for item in cart_items)
    return total 