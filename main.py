from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from app import app,db
from app.model import User, Item, Item_type, Colection, item_in_collection, User_Collection
from werkzeug.security import generate_password_hash

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
        
        if not user or user.verify_password(password):
            return redirect(url_for('login')), "<h1>Senha Incorreta Ou Usuario não cadastrado</h1>"
        
        login_user(user)

        return redirect(url_for("itens"))

    return render_template('login.html')

@app.route('/logout' , methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/itens/' , methods=['GET','POST'])
@login_required
def itens():
    return render_template('itens.html')
  

app.run(debug=True)