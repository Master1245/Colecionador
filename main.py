from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from app import app,db
from app.model import User, Item, Item_type, Colection, item_in_collection, User_Collection
from werkzeug.security import generate_password_hash,check_password_hash
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
    if current_user.is_authenticated:
        collection_id = []
        collections = []
        user = current_user.id
        collection = User_Collection.query.filter_by(user_id=user).all()
        for i in collection:
            collection_id.append(i.collection_id)
        for i in collection_id:
            collections.append(Colection.query.filter_by(id=i).first())
        return render_template('home.html', type=Item_type.query.all(), collection=collections) 
    else:
        return redirect(url_for('login', message="*Favor preencher todos os campos*"))
        
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
            if user.Token_reset != None:
                if user.Token_reset == password:
                    user.Token_reset = None
                    user.password = generate_password_hash("Trocar123")
                    db.session.commit()
                    return render_template('login.html', message='Sua senha é Trocar123 <br> FAVOR TROCAR A SENHA APOS FAZER LOGIN NOVAMENTE')
                else:
                    return render_template('login.html', message='Token inválido ou email invalido')

            if user.verify_password(password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                return render_template('login.html', message="Senha incorreta")
    except Exception as e:
        return render_template('login.html', message=e)
    return render_template('login.html', message="*Favor preencher todos os campos*")

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
    # SELECT I.name, I.hash FROM item_in_collection AS C, items AS I WHERE C.collection_id=1 AND C.item_id=I.id ORDER BY I.name
    itens_bd = item_in_collection.query.filter(item_in_collection.collection_id.in_(collections)).order_by(item_in_collection.item_id).all()
    itens = []
    for item in itens_bd:
        itens.append(item.item_id)
    itens_bd = Item.query.filter(Item.id.in_(itens)).all()
    img = []
    for iten in itens_bd:
        img.append(get_img(iten.hash))
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

@app.route("/forgotpassword" , methods=['GET','POST'])
def forgot_password():
    try:
        if request.method == "POST":
            email = request.form['email']
            if email:
                user = User.query.filter_by(email=email).first()
                if user:
                    token = generate_password_hash(user.email)
                    user.Token_reset = token
                    db.session.commit()
                    User.SendMail(token,email)
                else:
                    return render_template('forgotpassword.html', message="Email não cadastrado")
            else:
                return render_template('forgotpassword.html', message="Preencha todos os campos")
    except Exception as e:
        return render_template('forgot_password.html', message=e)
    return render_template('forgot_password.html')

@app.route("/changepassword" , methods=['GET','POST'])
def change_password():
    try:
        if request.method == "POST":
            email = request.form['email']
            senha_atual = request.form['password_atual']
            senha_nova = request.form['password_nova']
            if email and senha_atual and senha_nova:
                user = User.query.filter_by(email=email).first()
                if user:
                    if check_password_hash(user.password, senha_atual):
                        user.password = generate_password_hash(senha_nova)
                        db.session.commit()
                        return render_template('home.html', message="Senha alterada com sucesso")
                    else:
                        return render_template('change_password.html', message="Senha atual incorreta")
                else:
                    return render_template('change_password.html', message="Email não cadastrado")
    except Exception as e:
        render_template('change_password.html', message=e)
    return render_template('change_password.html')

@app.route("/get_collections" , methods=['GET'])
def get_collections():
    try:
        return "teste"
    except Exception as e:
        return e

@app.route("/post_collections", methods=['GET','POST'])
def post_collections():
    name = request.args.get('name', 0, type=str)
    description = request.args.get('description', 0, type=str)
    try:
        if name and description:
            collection = Colection(name, description)
            db.session.add(collection)
            db.session.commit()
            collection_id = Colection.query.filter_by(description=description).first().id
            user_Collection = User_Collection(current_user.id, collection_id)
            db.session.add(user_Collection)
            db.session.commit()
            return "True"
        else: 
            return "False"
    except Exception as e:
        return e
    



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)