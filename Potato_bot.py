import logging
import time
import chess

logging.basicConfig(filename="engine.log", level=logging.DEBUG, format='%(asctime)s - %(message)s')

# Sakk tábla inicializálása
board = chess.Board(chess.STARTING_FEN)

# Konfigurációs opciók
config = {
    "depth": 5,
    "time_limit": 10  # másodpercben
}

# Figuraértékek
piece_value = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Pozíciós értékek
position_values = {
    chess.BISHOP: [[-20, -10, -10, -10, -10, -10, -10, -20], [-10, 0, 0, 0, 0, 0, 0, -10], [-10, 0, 5, 10, 10, 5, 0, -10],
                   [-10, 5, 5, 10, 10, 5, 5, -10], [-10, 0, 10, 10, 10, 10, 0, -10], [-10, 10, 10, 10, 10, 10, 10, -10],
                   [-10, 5, 0, 0, 0, 0, 5, -10], [-20, -10, -10, -10, -10, -10, -10, -20]],
    chess.KNIGHT: [[-50, -40, -30, -30, -30, -30, -40, -50], [-40, -20, 0, 0, 0, 0, -20, -40],
                   [-30, 0, 10, 15, 15, 10, 0, -30], [-30, 5, 15, 20, 20, 15, 5, -30],
                   [-30, 0, 15, 20, 20, 15, 0, -30], [-30, 5, 10, 15, 15, 10, 5, -30],
                   [-40, -20, 0, 5, 5, 0, -20, -40], [-50, -40, -30, -30, -30, -30, -40, -50]],
    chess.PAWN: [[0, 0, 0, 0, 0, 0, 0, 0], [50, 50, 50, 50, 50, 50, 50, 50], [10, 10, 20, 30, 30, 20, 10, 10],
                 [5, 5, 10, 25, 25, 10, 5, 5], [0, 0, 0, 20, 20, 0, 0, 0], [5, -5, -10, 0, 0, -10, -5, 5],
                 [5, 10, 10, -20, -20, 10, 10, 5], [0, 0, 0, 0, 0, 0, 0, 0]],
    chess.ROOK: [[0, 0, 0, 0, 0, 0, 0, 0], [5, 10, 10, 10, 10, 10, 10, 5], [-5, 0, 0, 0, 0, 0, 0, -5],
                 [-5, 0, 0, 0, 0, 0, 0, -5], [-5, 0, 0, 0, 0, 0, 0, -5], [-5, 0, 0, 0, 0, 0, 0, -5],
                 [-5, 0, 0, 0, 0, 0, 0, -5], [0, 0, 0, 5, 5, 0, 0, 0]],
    chess.QUEEN: [[-20, -10, -10, -5, -5, -10, -10, -20], [-10, 0, 0, 0, 0, 0, 0, -10],
                  [-10, 0, 5, 5, 5, 5, 0, -10], [-5, 0, 5, 5, 5, 5, 0, -5], [0, 0, 5, 5, 5, 5, 0, -5],
                  [-10, 5, 5, 5, 5, 5, 0, -10], [-10, 0, 5, 0, 0, 0, 0, -10], [-20, -10, -10, -5, -5, -10, -10, -20]],
    "middlegame": [[-30, -40, -40, -50, -50, -40, -40, -30], [-30, -40, -40, -50, -50, -40, -40, -30],
                   [-30, -40, -40, -50, -50, -40, -40, -30], [-30, -40, -40, -50, -50, -40, -40, -30],
                   [-20, -30, -30, -40, -40, -30, -30, -20], [-10, -20, -20, -20, -20, -20, -20, -10],
                   [20, 20, 0, 0, 0, 0, 20, 20], [20, 30, 10, 0, 0, 10, 30, 20]],
    "endgame": [[-50, -40, -30, -20, -20, -30, -40, -50], [-30, -20, -10, 0, 0, -10, -20, -30],
                [-30, -10, 20, 30, 30, 20, -10, -30], [-30, -10, 30, 40, 40, 30, -10, -30],
                [-30, -10, 30, 40, 40, 30, -10, -30], [-30, -10, 20, 30, 30, 20, -10, -30],
                [-30, -30, 0, 0, 0, 0, -30, -30], [-50, -30, -30, -30, -30, -30, -30, -50]]
}

def calculate_phase(board):
    total_phase = 24
    current_phase = total_phase
    for piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
        current_phase -= len(board.pieces(piece_type, chess.WHITE))
        current_phase -= len(board.pieces(piece_type, chess.BLACK))
    return current_phase / total_phase

def evaluate_board(board, phase):
    evaluation = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_value[piece.piece_type]
            pos_value = position_values.get(piece.piece_type, [[0]*8]*8)[chess.square_rank(square)][chess.square_file(square)]
            if piece.color == chess.WHITE:
                evaluation += value + pos_value
            else:
                evaluation -= value + pos_value
    return evaluation

def alpha_beta_with_time(board, depth, alpha, beta, maximizing_player, end_time):
    if time.time() > end_time or depth == 0 or board.is_game_over():
        return evaluate_board(board, calculate_phase(board)), None
    best_move = None
    if maximizing_player:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = alpha_beta_with_time(board, depth-1, alpha, beta, False, end_time)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = alpha_beta_with_time(board, depth-1, alpha, beta, True, end_time)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# Beolvasás a GUI-ból (pl. UCI protokoll)
while True:
    line = input()
    if line == "uci":
        print("id name MyChessBot 1.0")
        print("id author YourName")
        print("uciok")
    elif line == "isready":
        print("readyok")
    elif line == "ucinewgame":
        board = chess.Board()
    elif line.startswith("position"):
        parts = line.split(" ")
        if "startpos" in parts:
            board = chess.Board()  # Alapállapot
            if "moves" in parts:
                moves_index = parts.index("moves")
                moves = parts[moves_index + 1:]
                for move in moves:
                    board.push(chess.Move.from_uci(move))
        elif "fen" in parts:
            fen = " ".join(parts[2:parts.index("moves")]) if "moves" in parts else " ".join(parts[2:])
            board = chess.Board(fen)
            if "moves" in parts:
                moves_index = parts.index("moves")
                moves = parts[moves_index + 1:]
                for move in moves:
                    board.push(chess.Move.from_uci(move))
        elif "moves" in parts:  # Csak lépések megadása alapállapotról
            board = chess.Board()
            moves_index = parts.index("moves")
            moves = parts[moves_index + 1:]
            for move in moves:
                board.push(chess.Move.from_uci(move))
    elif line == "go":
        end_time = time.time() + config["time_limit"]
        _, best_move = alpha_beta_with_time(board, depth=config["depth"], alpha=-float('inf'), beta=float('inf'),
                                            maximizing_player=board.turn, end_time=end_time)
        if best_move:
            print(f"bestmove {best_move.uci()}")
        else:
            print("info string Game over!")
    elif line.startswith("setoption"):
        parts = line.split(" ")
        option_name = parts[2]
        option_value = parts[4]
        if option_name == "depth":
            config["depth"] = int(option_value)
        elif option_name == "time_limit":
            config["time_limit"] = float(option_value)
    elif line == "quit":
        break
    else:
        print(f"Unknown command: {line}")





