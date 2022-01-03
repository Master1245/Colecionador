from typing import Collection
from boto3 import client
from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from app import app,db
from app.model import User, Item, Item_type, Colection, item_in_collection, User_Collection
from werkzeug.security import generate_password_hash
from app.AWS import upload_img, get_img
import os

Migrate(app, db)

@app.shell_context_processor
def make_chell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Item=Item,
        Item_type=Item_type,
        Colection=Colection,
        item_in_collection=item_in_collection,
        User_Collection=User_Collection
    )

@app.route('/' , methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/register' ,methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
     
        user = User(name, email, password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login' , methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user:
            return redirect(url_for('register'))
        if user.verify_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout' , methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/itens/' , methods=['GET','POST'])
@login_required
def itens():
    collections = []
    
    # SELECT C.collection_id FROM user_collection AS C WHERE user_id=1
    p = User_Collection.query.filter_by(user_id=current_user.id).all()
    for itens in p:
        collections.append(itens.collection_id)
    # SELECT I.name, I.hash 
    # FROM item_in_collection AS C, items AS I 
    # WHERE C.collection_id=1 AND C.item_id=I.id ORDER BY I.name
    itens_bd = item_in_collection.query.filter(item_in_collection.collection_id.in_(collections)).order_by(item_in_collection.item_id).all()
    itens = []
    for item in itens_bd:
        itens.append(item.item_id)
    itens_bd = Item.query.filter(Item.id.in_(itens)).all()
    img = []
    for iten in itens_bd:
        img.append(get_img(iten.hash))
    print(img)
    return render_template('itens.html' , img=img)
  
@app.route('/register_item' , methods=['GET','POST'])    
@login_required
def register_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        item_type = request.form['item_type']
        img = request.files['img']
        hash = generate_password_hash(name)
        item = Item(name, description, item_type, hash)
        db.session.add(item)
        db.session.commit() 
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath+ "/CARDS/", '',"img.jpg")
        img.save(upload_path)
        upload_img("img.jpg",hash)
        return redirect(url_for('itens'))

    return render_template('register_item.html')
    
app.run(debug=True)


# SELECT C.collection_id FROM user_collection AS C WHERE user_id=1

# SELECT I.name, I.hash FROM item_in_collection AS C, items AS I WHERE C.collection_id=1 AND C.item_id=I.id ORDER BY I.name