import os, csv
from flask import Flask, jsonify, request
from functools import wraps
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)

from .models import db, User, UserPokemon, Pokemon

# Configure Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MySecretKey'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config['JWT_HEADER_TYPE'] = ""
app.config['JWT_HEADER_NAME'] = "Cookie"


# Initialize App 
db.init_app(app)
app.app_context().push()
CORS(app)
jwt = JWTManager(app)

# Initializer Function to be used in both init command and /init route
def initialize_db():
  db.drop_all()
  db.create_all()

# ********** Routes **************
@app.route('/')
def index():
  return '<h1>Poke API v1.0</h1>'

@app.route('/init')
def init():
  initialize_db()
  return jsonify({"message": "Database initialized successfully"}), 200

@app.route('/pokemon')
def list_pokemon():
  pokemons = Pokemon.query.all()
  return jsonify([pokemon.get_json() for pokemon in pokemons]), 200

@app.route('/signup', methods=['POST'])
def signup():
  data = request.get_json()
  user = User(username=data['username'], email=data['email'])
  user.set_password(data['password'])
  try:
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 200
  except IntegrityError:
    return jsonify({"message": "Username or email already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
  data = request.get_json()
  user = User.query.filter_by(username=data['username']).first()
  if user and user.check_password(data['password']):
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200
  else:
    return jsonify({"message": "Invalid username or password"}), 401

@app.route('/mypokemon', methods=['POST'])
@jwt_required
def catch_pokemon():
  data = request.get_json()
  user_id = get_jwt_identity()
  user = User.query.get(user_id)
  pokemon = Pokemon.query.get(data['pokemon_id'])
  if not pokemon:
    return jsonify({"message": "Invalid Pokemon ID"}), 400
  user.catch_pokemon(data['pokemon_id'], data['name'])
  return jsonify({"message": "Pokemon caught successfully", "UserPokemon.id": user.pokemons[-1].id}), 200

@app.route('/mypokemon', methods=['GET'])
@jwt_required
def list_my_pokemon():
  user_id = get_jwt_identity()
  user_pokemons = UserPokemon.query.filter_by(user_id=user_id).all()
  return jsonify([pokemon.get_json() for pokemon in user_pokemons]), 200

@app.route('/mypokemon/<int:id>', methods=['GET'])
@jwt_required
def get_my_pokemon(id):
  user_id = get_jwt_identity()
  user_pokemon = UserPokemon.query.filter_by(user_id=user_id, id=id).first()
  if not user_pokemon:
    return jsonify({"message": "Invalid UserPokemon ID"}), 400
  return jsonify(user_pokemon.get_json()), 200

@app.route('/mypokemon/<int:id>', methods=['PUT'])
@jwt_required
def update_my_pokemon(id):
  user_id = get_jwt_identity()
  user = User.query.get(user_id)
  data = request.get_json()
  try:
    user.rename_pokemon(id, data['name'])
    return jsonify({"message": "Pokemon renamed successfully"}), 200
  except ValueError:
    return jsonify({"message": "Invalid UserPokemon ID or not owned by user"}), 400
 
@app.route('/mypokemon/<int:id>', methods=['DELETE'])
@jwt_required
def delete_my_pokemon(id):
  user_id = get_jwt_identity()
  user = User.query.get(user_id)
  try:
    user.release_pokemon(id)
    return jsonify({"message": "Pokemon released successfully"}), 200
  except ValueError:
    return jsonify({"message": "Invalid UserPokemon ID or not owned by user"}), 400

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81)
