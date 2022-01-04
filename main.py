from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from sqlalchemy import log
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
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            if name and email and password:
                user = User(name, email, password)
                db.session.add(user)
                db.session.commit()
            else: 
                return render_template('register.html', message="Preencha todos os campos")
            return redirect(url_for('login'))
    except Exception as e:
        if e.__class__.__name__ == 'IntegrityError':
            return render_template('register.html', message='Email já cadastrado')
        else:
            return render_template('register.html', message='Erro ao cadastrar usuário')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if not user:
                return render_template('login.html', message='Usuário não cadastrado')
            if user.verify_password(password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                return render_template('login.html', message="Senha incorreta")
    except Exception as e:
        return render_template('login.html', message=e)
    return render_template('login.html', message="Favor preencher todos os campos")

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
    collection_name = []
    collections = User_Collection.query.filter_by(user_id=User.query.filter_by(id=current_user.id).first().id).all()
    for iten in collections:
        collection_name.append(Colection.query.filter_by(id=iten.collection_id).first().name)
    try:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            item_type = request.form['type']
            collection = request.form['Colecao']
            img = request.files['img']
            hash = generate_password_hash(name)
            remove = ["<", ">", "Item_type ", "'"]
            for i in remove:
                item_type = item_type.replace(i, "")
            type = Item_type.query.filter_by(name=item_type).first().id
            colecao = Colection.query.filter_by(name=collection).first().id
            if name and description and item_type and img:
                item = Item(name, description, type, hash)
                db.session.add(item)
                db.session.commit()
                item = Item.query.filter_by(hash=hash).first().id
                collection = item_in_collection(item, colecao)
                db.session.add(collection)
                db.session.commit()
                basepath = os.path.dirname(__file__)
                upload_path = os.path.join(basepath+ "/CARDS/", '',"img.jpg")
                img.save(upload_path)
                upload_img("img.jpg",hash)
                return redirect(url_for('itens'))
            else:
                return render_template('register_item.html', message="Preencha todos os campos", collections=collection_name, type=Item_type.query.all())
    except Exception as e:
        print(e)
        return render_template('register_item.html', message=e, collections=collection_name, type=Item_type.query.all())
    return render_template('register_item.html', collections=collection_name, type=Item_type.query.all())
    

@app.route('/register_collection' , methods=['GET','POST'])
@login_required
def register_collection():
    try:
        if request.method == "POST":
            name = request.form['name']
            description = request.form['description']
            if name and description:
                collection = Colection(name, description)
                db.session.add(collection)
                db.session.commit()
                collection_id = Colection.query.filter_by(description=description).first().id
                user_Collection = User_Collection(current_user.id, collection_id)
                db.session.add(user_Collection)
                db.session.commit()
                return render_template("home.html")
            else: 
                return render_template('register_collection.html', message="Preencha todos os campos")
    except Exception as e:
        return render_template('register_collection.html', message=e)
    return render_template('register_collection.html', message="Favor preencher todos os campos")
    
@app.route('/register_type' , methods=['GET','POST'])
@login_required
def register_type():
    try:
        if request.method == "POST":
            name = request.form['name']
            if name:
                type = Item_type(name)
                db.session.add(type)
                db.session.commit()
                return render_template("home.html")
            else:
                return render_template('register_type.html', message="Preencha todos os campos")
    except Exception as e:
        return render_template('register_type.html', message=e)

    return render_template('register_type.html', message="Favor preencher todos os campos")
app.run(debug=True)
