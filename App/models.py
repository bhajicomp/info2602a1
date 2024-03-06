from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class UserPokemon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
  name = db.Column(db.String(50))

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(128))
  pokemons = db.relationship('UserPokemon', backref='user', lazy=True)

  def catch_pokemon(self, pokemon_id, name):
    new_pokemon = UserPokemon(user_id=self.id, pokemon_id=pokemon_id, name=name)
    db.session.add(new_pokemon)
    db.session.commit()

  def release_pokemon(self, pokemon_id, name):
    pokemon = UserPokemon.query.filter_by(user_id=self.id, pokemon_id=pokemon_id, name=name).first()
    if pokemon:
      db.session.delete(pokemon)
      db.session.commit()

  def rename_pokemon(self, pokemon_id, name):
    pokemon = UserPokemon.query.filter_by(user_id=self.id, pokemon_id=pokemon_id).first()
    if pokemon:
      pokemon.name = name
      db.session.commit()

  def set_password(self, password):
    self.password = generate_password_hash(password)
    db.session.commit()

  def check_password(self, password):
    return check_password_hash(self.password, password)

class Pokemon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  pass
