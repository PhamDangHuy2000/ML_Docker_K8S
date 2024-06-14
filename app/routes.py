from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sklearn.neighbors import NearestNeighbors
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@postgres-service/recommender'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    new_user = User(name=name, email=email)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    new_product = Product(name=name, category=category, price=price)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('products'))

@app.route('/recommend/<int:user_id>')
def recommend(user_id):
    user = User.query.get(user_id)
    products = Product.query.all()

    product_data = np.array([[p.id, p.category, p.price] for p in products])
    model = NearestNeighbors(n_neighbors=3)
    model.fit(product_data[:, 1:])
    distances, indices = model.kneighbors(product_data[product_data[:, 0] == user_id, 1:])

    recommendations = [Product.query.get(int(product_data[i, 0])) for i in indices[0]]
    return render_template('recommend.html', user=user, recommendations=recommendations)

