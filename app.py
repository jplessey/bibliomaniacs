from flask import Flask, flash, render_template, request, redirect, url_for
from flask import session as user_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_marshmallow import Marshmallow
from database_setup import Book, User, Base, engine
from functools import wraps


# Init app
app = Flask(__name__)

# Database
engine = create_engine('sqlite:///books-collection.db', connect_args={'check_same_thread': False})
Base.metadata.bind = create_engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
ma = Marshmallow(app)
app.secret_key = "la_cookie"


# Users Schema
class UsersSchema(ma.Schema):
    """Users database schema"""
    class Meta:
        fields = ('id', 'username', 'password')

# Init users schema
users_schema = UsersSchema(many=True)


# Books Schema
class BooksSchema(ma.Schema):
    """Books database schema"""
    class Meta:
        fields = ('id', 'title', 'author', 'genre', 'read', 'user_id')

# Init books schema
books_schema = BooksSchema(many=True)


# User sign up
@app.route('/signup', methods=['POST'])
def signup_post():
    if request.form['username'] and request.form['password']:
        username = request.form['username']
        password = request.form['password']
        user = session.query(User).filter_by(username=username).first()
        if user:
            flash('Username already exist. Try again!')
            return render_template("login.html")
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Password and confirmation did not match. Try again!')
            return render_template("login.html")
        new_user = User(
            username=request.form['username'],
            password=request.form['password'],
        )
        session.add(new_user)
        session.commit()
        flash(f'Welcome {username}, sign in to start your book collection!')
        return render_template("login.html")
    flash('Need to enter username and password')
    return render_template("login.html")


# User sign in process
@app.route('/', methods=['GET', 'POST'])
def signin_post():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = session.query(User).filter_by(username=username).first()
        if user:
            if user.password == password:
                user_session['logged_in'] = True
                user_session['user_id'] = user.id
                user_session['username'] = username
                flash(f'Welcome {username}!')
                return redirect(url_for('show_books'))
            else:
                flash('Incorrect password')
                return render_template("login.html")
        else:
            flash('User not registered. Please Sign Up')
            return render_template("login.html")
    return render_template("login.html")


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in user_session:
            return f(*args, **kwargs)
        else:
            flash('Access denied, please Sign In', 'danger')
            return redirect(url_for('signin_post'))
    return wrap


# Index
@app.route('/')
def user_login():
    """User login page"""
    return render_template("login.html")


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    user_session.clear()
    return redirect(url_for('signin_post'))


# Show all books
@app.route('/books')
@is_logged_in
def show_books():
    """Show books from database"""
    user_id = user_session['user_id']
    books = reversed(session.query(Book).filter_by(user_id=user_id).all())
    print(books)
    if not books:
        flash('Add some books to start your collection!')
    return render_template("books.html", books=books)


# Add new book
@app.route('/books', methods=['GET', 'POST'])
@is_logged_in
def new_book():
    """Add book to database"""
    if request.method == 'POST':
        if request.form['name'] and request.form['author']:
            try:
                read = bool(request.form['read'])
            except KeyError:
                read = False
            user_id = user_session['user_id']
            a_new_book = Book(
                title=request.form['name'],
                author=request.form['author'],
                genre=request.form['genre'],
                read=read,
                user_id=user_id
            )
            session.add(a_new_book)
            session.commit()
            return redirect(url_for('show_books'))
        flash('Need to enter at least Title and Author of the book')
        return redirect(url_for('show_books'))
    return redirect(url_for('show_books'))


# Edit book
@app.route('/books/<int:book_id>/edit/', methods=['GET', 'POST'])
@is_logged_in
def edit_book(book_id):
    """Edit book from database"""
    edited_book = session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_book.title = request.form['name']
            edited_book.author = request.form['author']
            edited_book.genre = request.form['genre']
            try:
                edited_book.read = bool(request.form['read'])
            except KeyError:
                pass
            session.commit()
            return redirect(url_for('show_books'))
    return redirect(url_for('show_books'))


#Delete book
@app.route('/books/<int:book_id>/delete/', methods=['GET', 'POST'])
@is_logged_in
def delete_book(book_id):
    """Delete book from database"""
    book_to_delete = session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        session.delete(book_to_delete)
        session.commit()
        return redirect(url_for('show_books'))
    return redirect(url_for('show_books'))


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=80, debug=True)
