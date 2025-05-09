from functools import wraps
from flask import session, redirect, url_for, flash
from models import User, db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите для доступа к этой странице')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите для доступа к этой странице')
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('У вас нет прав для доступа к этой странице')
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


def register_user(username, email, password, is_seller=False):
    if User.query.filter_by(username=username).first():
        return False, 'Пользователь с таким именем уже существует'
    if User.query.filter_by(email=email).first():
        return False, 'Email уже зарегистрирован'

    user = User(username=username, email=email, is_seller=is_seller)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return True, 'Регистрация успешна'


def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        return True, 'Вход выполнен успешно'
    return False, 'Неверное имя пользователя или пароль'


def logout_user():
    session.clear()
    return 'Выход выполнен успешно'
