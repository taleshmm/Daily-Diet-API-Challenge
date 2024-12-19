from datetime import datetime

import bcrypt
from flask import Flask, jsonify, request
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)

from database import db
from models.diet import Diet
from models.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = "b1f6d8d9d9e4d3e03a6f61bdb5e7a66aa8e4b3d3c5c7f7f8a9b0d1e2f3a4b5c6"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/diet-daily'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

#view login
login_manager.login_view = 'login'
    
@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            return jsonify({"message": "Authentication with success"})
        
    return jsonify({"message": "Invalid Credentials"}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout did with success!"})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": f"User created with ID {user.id} successfully!"})
    
    return jsonify({"message": "Credentials invalid!"}), 401

@app.route('/diet', methods=['POST'])
@login_required
def create_diet():
    datas = request.json
    name = datas.get('name')
    description = datas.get('description')
    date = datas.get('date')
    is_inside_diet = datas.get('is_inside_diet')
    user_id = datas.get('user_id')
    
    if user_id != current_user.id:
        return jsonify({"message": "Action not allowed"}), 403
    
    if name and user_id:   
        check_date = datetime.strptime(date, "%d/%m/%Y %H:%M:%S") if date  else datetime.now() 
        diet = Diet(name=name, description=description, date=check_date, is_inside_diet=is_inside_diet, user_id=user_id)
        
        db.session.add(diet)
        db.session.commit()
        return jsonify({"message": f"Diet created with ID {diet.id} successfully!"})
    
    return jsonify({"message": "Credentials invalid!"}), 401

@app.route('/diet/<int:id_diet>', methods=["PUT"])
@login_required
def uptade_diet(id_diet):
    data = request.json
    diet = Diet.query.get(id_diet)
    
    if diet: 
        if diet.user_id != current_user.id:
            return jsonify({"message": "Action not allowed"}), 403

        new_date = data.get("date")
        if new_date:
            new_date = datetime.strptime(new_date, "%d/%m/%Y %H:%M:%S")
        diet.name = data.get("name")
        diet.description = data.get("description")
        diet.date =  new_date if new_date else diet.date
        diet.is_inside_diet = data.get("is_inside_diet")
        db.session.commit()
        return jsonify({"message": "Diet updated with success!"})
    
    return jsonify({"message": "Diet not found"}), 404
    
    

if __name__ == '__main__':
    app.run(debug=True)