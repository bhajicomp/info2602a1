from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class UserPokemon(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'))
  name = db.Column(db.String(50))

  def get_json(self):
    return {
      'id': self.id,
      'user_id': self.user_id,
      'pokemon_id': self.pokemon_id,
      'name': self.name
    }

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
  name = db.Column(db.String(50))
  attack = db.Column(db.Integer)
  defense = db.Column(db.Integer)
  hp = db.Column(db.Integer)
  height = db.Column(db.Integer)
  sp_attack = db.Column(db.Integer)
  sp_defense = db.Column(db.Integer)
  speed = db.Column(db.Integer)
  type1 = db.Column(db.String(50))
  type2 = db.Column(db.String(50))

  def get_json(self):
    return {
      'id': self.id,
      'name': self.name,
      'attack': self.attack,
      'defense': self.defense,
      'hp': self.hp,
      'height': self.height,
      'sp_attack': self.sp_attack,
      'sp_defense': self.sp_defense,
      'speed': self.speed,
      'type1': self.type1,
      'type2': self.type2
    }
