from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditForm
from app.models import User, Book


@app.route('/')
@app.route('/index')
@login_required
def index():
    books = Book.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', title='Home', books=books)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditForm()
    existing_data = []
    for i in range(5):
        j = Book.query.filter_by(user_id=current_user.id).filter_by(rank=i+1).first()
        existing_data.append(j)
    if form.validate_on_submit():
        form_data = [
            (form.title1.data, form.author1.data),
            (form.title2.data, form.author2.data),
            (form.title3.data, form.author3.data),
            (form.title4.data, form.author4.data),
            (form.title5.data, form.author5.data)
        ]
        for i in range(5):
            # b = Book.query.filter_by(user_id=current_user.id).filter_by(rank=i+1).first()
            b = existing_data[i]
            if b:
                b.title = form_data[i][0]
                b.author = form_data[i][1]
                db.session.commit()
            else:
                b = Book(user_id=current_user.id, rank=i+1, title=form_data[i][0], author=form_data[i][1])
                db.session.add(b)
                db.session.commit()
        return(redirect(url_for('index')))
    return(render_template('edit.html', title='Edit', form=form, existing_data=existing_data))

