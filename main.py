from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from app import app,db
from app.model import User, Item, Item_type, Colection, item_in_collection, User_Collection
from werkzeug.security import generate_password_hash,check_password_hash
from app.AWS import upload_img, get_img, delete_img
from flask import jsonify
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
        return render_template('home.html', types=Item_type.query.all(), collections=collections) 
    else:
        return redirect(url_for('login'))
        
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
                return render_template('user/register.html', message="Preencha todos os campos")
            return redirect(url_for('login'))
    except Exception as e:
        if e.__class__.__name__ == 'IntegrityError':
            return render_template('user/register.html', message='Email já cadastrado')
        else:
            return render_template('user/register.html', message='Erro ao cadastrar usuário')
    return render_template('user/register.html')

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
                    return render_template('user/forgotpassword.html', message="Email não cadastrado")
            else:
                return render_template('user/forgotpassword.html', message="Preencha todos os campos")
    except Exception as e:
        return render_template('user/forgot_password.html', message=e)
    return render_template('user/forgot_password.html')

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
                        return render_template('user/change_password.html', message="Senha atual incorreta")
                else:
                    return render_template('user/change_password.html', message="Email não cadastrado")
    except Exception as e:
        render_template('user/change_password.html', message=e)
    return render_template('user/change_password.html')

@app.route("/get_collections" , methods=['GET'])
def get_collections():
    try:
        collection_id = []
        collections = []
        user = current_user.id
        collection = User_Collection.query.filter_by(user_id=user).all()
        for i in collection:
            collection_id.append(i.collection_id)
        for i in collection_id:
            collections.append(Colection.query.filter_by(id=i).all())
        result_collections = []
        for i in collections:
            res = {'description':i[0].description, 'name':i[0].name, 'id':i[0].id}
            result_collections.append(res)
        return jsonify(result_collections)
    except Exception as e:
        return e

@app.route("/get_types" , methods=['GET'])
def get_types():
    try:
        types = []
        for i in Item_type.query.all():
            result = {'name': i.name, 'id': i.id}
            types.append(result)
        return jsonify(types)
    except Exception as e:
        return e

@app.route("/get_item" , methods=['GET','POST'])
@login_required
def get_item():
    try:
        collection = []
        collection_user = request.args.get('collection_id', 0, type=int)
        itens_in_collection = item_in_collection.query.filter_by(collection_id=collection_user).all()
        for i in itens_in_collection:
            item = Item.query.filter_by(id=i.item_id).first()
            img_link = get_img(item.hash)
            result = {'id': item.id,'name': item.name, 'description': item.description, 'type': item.type_id, 'link_img': img_link}	
            collection.append(result)
        return jsonify(collection)
    except Exception as e:
        return e

@app.route('/post_item' , methods=['GET','POST'])    
@login_required
def post_item():
    try:
        if request.method == "POST":
            request.files['img_item'].save("./CARDS/" + "img.jpg")
            hash_img = generate_password_hash(request.files['img_item'].filename)
            name = request.form['name_item']
            description = request.form['description_item']
            type_id = request.form['type_select']
            collection_id = request.form['colecao_select']
            type_id = Item_type.query.filter_by(id=type_id).first()
            item = Item(name, description, type_id.id, hash_img)
            db.session.add(item)
            db.session.commit()
            collection = item_in_collection(item.id, collection_id)
            db.session.add(collection)
            db.session.commit()
            upload_img(hash=hash_img,img_name="img.jpg")
            return "201"
        return "401"
    except Exception as e:
        return e

@app.route('/post_type' , methods=['GET','POST'])
@login_required
def post_type():
    try:
        name = request.args.get('name', 0, type=str)
        if name:
            type = Item_type(name)
            db.session.add(type)
            db.session.commit()
            return '201'
        else:
            return '400'
    except Exception as e:
        return e

@app.route("/post_collection", methods=['GET','POST'])
@login_required
def post_collection():
    try:
        name = request.args.get('name', 0, type=str)
        description = request.args.get('description', 0, type=str)
        if name and description:
            collection = Colection(name, description)
            db.session.add(collection)
            db.session.commit()
            collection_id = Colection.query.filter_by(description=description).first().id
            user_Collection = User_Collection(current_user.id, collection_id)
            db.session.add(user_Collection)
            db.session.commit()
            return "201"
        else:
            return "400"
    except Exception as e:
        return e

@app.route("/delete_item", methods=['GET','POST'])
@login_required
def delete_item():
    try:
        item_id = request.args.get('item_id', 0, type=int)
        if item_id:
            item = Item.query.filter_by(id=item_id).first()
            delete_img(item.hash)
            db.session.delete(item)
            db.session.commit()
            return "201"
        else:
            return "400"
    except Exception as e:
        return e

@app.route("/delete_collection", methods=['GET','POST'])
@login_required
def delete_collection():
    try:
        collection_id = request.args.get('collection_id', 0, type=int)
        if collection_id:
            collection = Colection.query.filter_by(id=collection_id).first()
            db.session.delete(collection)
            db.session.commit()
            return "201"
        else:
            return "400"
    except Exception as e:
        return e

@app.route("/update_item", methods=['GET','POST'])
@login_required
def update_item():
    try:
        item_id = request.args.get('item_id', 0, type=int)
        name = request.args.get('name', 0, type=str)
        description = request.args.get('description', 0, type=str)
        if item_id and name and description:
            item = Item.query.filter_by(id=item_id).first()
            item.name = name
            item.description = description
            db.session.commit()
            return "201"
        else:
            return "400"
    except Exception as e:
        return e

@app.route("/update_collection", methods=['GET','POST'])
@login_required
def update_collection():
    try:
        collection_id = request.args.get('collection_id', 0, type=int)
        name = request.args.get('name', 0, type=str)
        description = request.args.get('description', 0, type=str)
        if collection_id and name and description:
            collection = Colection.query.filter_by(id=collection_id).first()
            collection.name = name
            collection.description = description
            db.session.commit()
            return "201"
        else:
            return "400"
    except Exception as e:
        return e

@app.route("/inventory" , methods=['GET','POST'])
@login_required
def inventory():
    try:
        return render_template('inventory.html')
    except Exception as e:
        return e

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)