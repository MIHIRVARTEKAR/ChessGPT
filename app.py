from flask import Flask, render_template, request, jsonify, session
import chess
import chess.svg
import uuid
import io
import sys
import random

app = Flask(__name__)
app.secret_key = 'replace_with_strong_random_secret'

board_store = {}

def get_board():
    session_id = session.get('session_id')
    if not session_id or session_id not in board_store:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        board_store[session_id] = chess.Board()
    return board_store[session_id]

def move_piece(start, end, board):
    try:
        move = chess.Move.from_uci(start + end)
        if move in board.legal_moves:
            board.push(move)
            return True
    except:
        pass
    return False

def make_computer_move(board):
    if board.turn == chess.BLACK:
        legal_moves = list(board.legal_moves)
        if legal_moves:
            move = random.choice(legal_moves)
            board.push(move)
            print(f"Computer moved: {move.uci()}")
            return True
    return False

def execute_user_code(user_code, board):
    global_scope = {'move_piece': lambda start, end: move_piece(start, end, board)}
    local_scope = {}
    try:
        exec(user_code, global_scope, local_scope)
        if board.turn == chess.BLACK:
            make_computer_move(board)
        return "Success", board.fen()
    except Exception as e:
        return f"Error: {str(e)}", None

@app.route('/')
def index():
    board = get_board()
    return render_template('index.html', board_svg=chess.svg.board(board=board))

@app.route('/move', methods=['POST'])
def move():
    board = get_board()
    user_code = request.form.get("code", "")
    if not user_code:
        return jsonify({"result": "Error: No code provided", "fen": board.fen()})
    result, fen = execute_user_code(user_code, board)
    return jsonify({"result": result, "fen": fen, "board_svg": chess.svg.board(board=board)})

@app.route('/reset', methods=['POST'])
def reset():
    session_id = session.get('session_id')
    if session_id in board_store:
        board_store[session_id] = chess.Board()
    return jsonify({"result": "Board reset", "fen": board_store[session_id].fen(), "board_svg": chess.svg.board(board=board_store[session_id])})

if __name__ == '__main__':
    app.run(debug=True)
