from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Skateboard
from auth import login_required, register_user, login_user, logout_user
from skateboards import (
    get_all_skateboards, create_skateboard, get_skateboard_by_id,
    update_skateboard, delete_skateboard, search_skateboards,
    get_skateboards_by_brand, get_skateboards_by_price_range,
    get_skateboards_in_stock, update_stock
)
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

def get_user(user_id):
    return User.query.get(user_id)

app.jinja_env.globals.update(get_user=get_user)

def init_db():
    with app.app_context():
        # Создаем все таблицы
        db.drop_all()  # Удаляем все существующие таблицы
        db.create_all()  # Создаем таблицы заново
        # Добавляем примеры скейтбордов только если их нет
        if Skateboard.query.count() == 0:
            sample_skateboards = Skateboard.get_sample_skateboards()
            db.session.add_all(sample_skateboards)
            db.session.commit()

# Инициализируем базу данных при запуске
init_db()

@app.route('/')
def index():
    skateboards = get_all_skateboards()
    return render_template('index.html', skateboards=skateboards)


@app.route('/catalog')
def catalog():
    query = request.args.get('query', '')
    brand = request.args.get('brand')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    if query:
        skateboards = search_skateboards(query)
    elif brand:
        skateboards = get_skateboards_by_brand(brand)
    elif min_price is not None and max_price is not None:
        skateboards = get_skateboards_by_price_range(min_price, max_price)
    else:
        skateboards = get_all_skateboards()

    return render_template('catalog.html', skateboards=skateboards)


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


@app.route('/skateboard/<int:skateboard_id>')
def skateboard_detail(skateboard_id):
    skateboard = get_skateboard_by_id(skateboard_id)
    return render_template('skateboard_detail.html', skateboard=skateboard)


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


if __name__ == '__main__':
    app.run(debug=True)
