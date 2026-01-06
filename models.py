from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    games_as_player1 = db.relationship('Game', foreign_keys='Game.player1_id', backref='player1', lazy=True)
    games_as_player2 = db.relationship('Game', foreign_keys='Game.player2_id', backref='player2', lazy=True)
    moves = db.relationship('Move', backref='player', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    player1_color = db.Column(db.String(20), nullable=True)
    player2_color = db.Column(db.String(20), nullable=True)
    current_turn = db.Column(db.Integer, default=1)
    board_state = db.Column(db.Text, default='{"grid": [[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]}')
    status = db.Column(db.String(20), default='waiting')
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    moves = db.relationship('Move', backref='game', lazy=True)
    winner = db.relationship('User', foreign_keys=[winner_id])
    
    def get_board(self):
        return json.loads(self.board_state)
    
    def set_board(self, board_dict):
        self.board_state = json.dumps(board_dict)

class Move(db.Model):
    __tablename__ = 'moves'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    move_data = db.Column(db.Text, nullable=False)
    move_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)