from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Game, Move
from config import Config
from game_logic import check_win, is_valid_move
import json

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    my_games = Game.query.filter(
        (Game.player1_id == current_user.id) | (Game.player2_id == current_user.id)
    ).order_by(Game.updated_at.desc()).all()
    
    active_games = [g for g in my_games if g.status in ['waiting', 'active']]
    completed_games = [g for g in my_games if g.status == 'completed']
    
    return render_template('dashboard.html', active_games=active_games, completed_games=completed_games)

@app.route('/game/create', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        opponent_username = request.form.get('opponent_username')
        player_color = request.form.get('color')
        
        opponent = User.query.filter_by(username=opponent_username).first()
        
        if not opponent:
            flash('User not found')
            return redirect(url_for('dashboard'))
        
        if opponent.id == current_user.id:
            flash('Cannot play against yourself')
            return redirect(url_for('dashboard'))
        
        game = Game(player1_id=current_user.id, player1_color=player_color)
        db.session.add(game)
        db.session.commit()
        
        flash(f'Game created! Waiting for {opponent_username} to join.')
        return redirect(url_for('game_view', game_id=game.id))
    
    return render_template('dashboard.html')

@app.route('/game/<int:game_id>')
@login_required
def game_view(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.player1_id != current_user.id and game.player2_id != current_user.id:
        if game.status == 'waiting' and game.player2_id is None:
            return redirect(url_for('join_game', game_id=game_id))
        flash('You are not a player in this game')
        return redirect(url_for('dashboard'))
    
    return render_template('game.html', game=game)

@app.route('/game/<int:game_id>/join', methods=['GET', 'POST'])
@login_required
def join_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.status != 'waiting':
        flash('Game is not available')
        return redirect(url_for('dashboard'))
    
    if game.player1_id == current_user.id:
        flash('This is your game')
        return redirect(url_for('game_view', game_id=game_id))
    
    if request.method == 'POST':
        player_color = request.form.get('color')
        
        if player_color == game.player1_color:
            flash('Color already taken, please choose another')
            return render_template('join_game.html', game=game)
        
        game.player2_id = current_user.id
        game.player2_color = player_color
        game.status = 'active'
        db.session.commit()
        
        return redirect(url_for('game_view', game_id=game_id))
    
    return render_template('join_game.html', game=game)

@app.route('/game/<int:game_id>/move', methods=['POST'])
@login_required
def make_move(game_id):
    game = Game.query.get_or_404(game_id)
    
    if game.status != 'active':
        return jsonify({'error': 'Game is not active'}), 400
    
    current_player = 1 if game.player1_id == current_user.id else 2
    
    if game.current_turn != current_player:
        return jsonify({'error': 'Not your turn'}), 400
    
    moves_data = request.json.get('moves')
    
    if not moves_data or len(moves_data) != 2:
        return jsonify({'error': 'Must place exactly 2 tiles'}), 400
    
    board = game.get_board()
    
    for move in moves_data:
        row, col, tile_type = move['row'], move['col'], move['type']
        
        if not is_valid_move(board, row, col):
            return jsonify({'error': 'Invalid move'}), 400
        
        if tile_type == 'path':
            board['grid'][row][col] = current_player
        elif tile_type == 'block':
            board['grid'][row][col] = 3
    
    game.set_board(board)
    
    move_record = Move(
        game_id=game.id,
        player_id=current_user.id,
        move_data=json.dumps(moves_data),
        move_number=Move.query.filter_by(game_id=game.id).count() + 1
    )
    db.session.add(move_record)
    
    winner = check_win(board)
    if winner:
        game.status = 'completed'
        game.winner_id = game.player1_id if winner == 1 else game.player2_id
    else:
        game.current_turn = 2 if current_player == 1 else 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'board': board,
        'current_turn': game.current_turn,
        'winner': winner,
        'status': game.status
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)