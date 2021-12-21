from flask import render_template, request, redirect, url_for
from flask_migrate import Migrate
from app import app,db
from app.model import User

Migrate(app, db)

@app.shell_context_processor
def make_chell_context():
    return dict(
        app=app,
        db=db,
        User=User,
    )

@app.route('/' ,methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/register' ,methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
    
    if name and email and password: 
        user = User(name, email, password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login' , methods=['GET','POST'])
def login():
    return render_template('login.html')

app.run(debug=True)