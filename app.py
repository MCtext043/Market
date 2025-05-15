from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Skateboard
from auth import login_required, register_user, login_user, logout_user
from skateboards import (
    get_all_skateboards, create_skateboard, get_skateboard_by_id,
    update_skateboard, delete_skateboard, search_skateboards,
    get_skateboards_by_brand, get_skateboards_by_price_range,
    get_skateboards_in_stock, update_stock, get_all_brands
)
from cart import (
    add_to_cart, remove_from_cart, update_cart_item_quantity,
    get_cart_items, get_cart_total
)
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def get_user(user_id):
    return User.query.get(user_id)


app.jinja_env.globals.update(get_user=get_user)


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        if Skateboard.query.count() == 0:
            sample_skateboards = Skateboard.get_sample_skateboards()
            db.session.add_all(sample_skateboards)
            db.session.commit()


init_db()


@app.route('/')
def index():
    skateboards = get_all_skateboards()
    return render_template('index.html', skateboards=skateboards)


@app.route('/catalog')
def catalog():
    filters = {}
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    brand = request.args.get('brand')
    in_stock = request.args.get('in_stock') == 'true'

    if min_price is not None:
        filters['min_price'] = min_price
    if max_price is not None:
        filters['max_price'] = max_price
    if brand:
        filters['brand'] = brand
    if in_stock:
        filters['in_stock'] = True
    sort_order = request.args.get('sort_order', 'asc')
    current_sort = {'by': 'price', 'order': sort_order}
    brands = get_all_brands()
    skateboards = get_all_skateboards(filters, 'price', sort_order)
    return render_template('catalog.html',
                           skateboards=skateboards,
                           brands=brands,
                           current_filters=filters,
                           current_sort=current_sort)


@app.route('/skateboard/<int:skateboard_id>')
def skateboard_detail(skateboard_id):
    skateboard = get_skateboard_by_id(skateboard_id)
    return render_template('skateboard_detail.html', skateboard=skateboard)


@app.route('/skateboard/<int:skateboard_id>/add_to_cart', methods=['POST'])
@login_required
def add_to_cart_route(skateboard_id):
    user = User.query.get(session['user_id'])
    if user.is_seller:
        flash('Продавцы не могут добавлять товары в корзину')
        return redirect(url_for('catalog'))

    quantity = int(request.form.get('quantity', 1))
    success, message = add_to_cart(user.id, skateboard_id, quantity)
    flash(message)
    return redirect(url_for('catalog'))


@app.route('/cart')
@login_required
def cart():
    user = User.query.get(session['user_id'])
    if user.is_seller:
        flash('У продавцов нет корзины')
        return redirect(url_for('index'))

    cart_items = get_cart_items(user.id)
    total = get_cart_total(user.id)
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/cart/update/<int:skateboard_id>', methods=['POST'])
@login_required
def update_cart(skateboard_id):
    user = User.query.get(session['user_id'])
    if user.is_seller:
        flash('У продавцов нет корзины')
        return redirect(url_for('index'))

    quantity = int(request.form.get('quantity', 1))
    success, message = update_cart_item_quantity(user.id, skateboard_id, quantity)
    flash(message)
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:skateboard_id>', methods=['POST'])
@login_required
def remove_from_cart_route(skateboard_id):
    user = User.query.get(session['user_id'])
    if user.is_seller:
        flash('У продавцов нет корзины')
        return redirect(url_for('index'))

    success, message = remove_from_cart(user.id, skateboard_id)
    flash(message)
    return redirect(url_for('cart'))


@app.route('/add_skateboard', methods=['GET', 'POST'])
@login_required
def add_skateboard():
    user = User.query.get(session['user_id'])
    if not user.is_seller:
        flash('Только продавцы могут добавлять товары')
        return redirect(url_for('catalog'))

    if request.method == 'POST':
        name = request.form['name']
        brand = request.form['brand']
        price = float(request.form['price'])
        description = request.form['description']
        image_url = request.form['image_url']
        stock = int(request.form['stock'])

        skateboard = create_skateboard(
            name=name,
            brand=brand,
            price=price,
            description=description,
            image_url=image_url,
            stock=stock
        )

        flash('Скейтборд успешно добавлен!')
        return redirect(url_for('catalog'))

    return render_template('add_skateboard.html')


@app.route('/skateboard/<int:skateboard_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_skateboard(skateboard_id):
    skateboard = get_skateboard_by_id(skateboard_id)

    if request.method == 'POST':
        update_skateboard(
            skateboard_id,
            name=request.form['name'],
            brand=request.form['brand'],
            price=float(request.form['price']),
            description=request.form['description'],
            image_url=request.form['image_url'],
            stock=int(request.form['stock'])
        )
        flash('Скейтборд успешно обновлен!')
        return redirect(url_for('skateboard_detail', skateboard_id=skateboard_id))

    return render_template('edit_skateboard.html', skateboard=skateboard)


@app.route('/skateboard/<int:skateboard_id>/delete', methods=['POST'])
@login_required
def delete_skateboard_route(skateboard_id):
    delete_skateboard(skateboard_id)
    flash('Скейтборд успешно удален!')
    return redirect(url_for('catalog'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success, message = login_user(username, password)
        flash(message)
        if success:
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_seller = 'is_seller' in request.form
        success, message = register_user(username, email, password, is_seller)
        flash(message)
        if success:
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    message = logout_user()
    flash(message)
    return redirect(url_for('index'))


@app.route('/api/skateboards', methods=['GET'])
def api_get_skateboards():
    filters = {}
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    brand = request.args.get('brand')
    in_stock = request.args.get('in_stock') == 'true'

    if min_price is not None:
        filters['min_price'] = min_price
    if max_price is not None:
        filters['max_price'] = max_price
    if brand:
        filters['brand'] = brand
    if in_stock:
        filters['in_stock'] = True

    sort_order = request.args.get('sort_order', 'asc')
    skateboards = get_all_skateboards(filters, 'price', sort_order)
    
    return jsonify([{
        'id': skateboard.id,
        'name': skateboard.name,
        'brand': skateboard.brand,
        'price': skateboard.price,
        'description': skateboard.description,
        'image_url': skateboard.image_url,
        'stock': skateboard.stock
    } for skateboard in skateboards])


@app.route('/api/skateboards/<int:skateboard_id>', methods=['GET'])
def api_get_skateboard(skateboard_id):
    skateboard = get_skateboard_by_id(skateboard_id)
    return jsonify({
        'id': skateboard.id,
        'name': skateboard.name,
        'brand': skateboard.brand,
        'price': skateboard.price,
        'description': skateboard.description,
        'image_url': skateboard.image_url,
        'stock': skateboard.stock
    })


if __name__ == '__main__':
    app.run(debug=True)
