import chess
import tkinter as tk

SQUARE_SIZE = 80
BOARD_COLOR_1 = "#F0D9B5"
BOARD_COLOR_2 = "#B58863"

board = chess.Board()
edit_mode = False
flip = False

drag_piece = None
drag_from = None
drag_x = drag_y = 0

WHITE_MODE = "human"
BLACK_MODE = "human"

PIECE_LIBRARY = [
    chess.Piece(chess.QUEEN, chess.WHITE),
    chess.Piece(chess.ROOK, chess.WHITE),
    chess.Piece(chess.BISHOP, chess.WHITE),
    chess.Piece(chess.KNIGHT, chess.WHITE),
    chess.Piece(chess.PAWN, chess.WHITE),
    chess.Piece(chess.KING, chess.WHITE),
    chess.Piece(chess.QUEEN, chess.BLACK),
    chess.Piece(chess.ROOK, chess.BLACK),
    chess.Piece(chess.BISHOP, chess.BLACK),
    chess.Piece(chess.KNIGHT, chess.BLACK),
    chess.Piece(chess.PAWN, chess.BLACK),
    chess.Piece(chess.KING, chess.BLACK),
]

root = tk.Tk()
root.title("Chess Sandbox + Bot + Flip")

canvas = tk.Canvas(root, width=8*SQUARE_SIZE+200, height=8*SQUARE_SIZE+40)
canvas.grid(row=0, column=0, rowspan=20)

panel = tk.Frame(root)
panel.grid(row=0, column=1, padx=10)

def evaluate(board):
    values = {chess.PAWN:1, chess.KNIGHT:3, chess.BISHOP:3, chess.ROOK:5, chess.QUEEN:9, chess.KING:0}
    score = 0
    for p in values:
        score += len(board.pieces(p, chess.WHITE))*values[p]
        score -= len(board.pieces(p, chess.BLACK))*values[p]
    return score

def minimax(board, depth, alpha, beta, maximizing):
    if depth==0 or board.is_game_over():
        return evaluate(board)
    if maximizing:
        value = -9999
        for move in board.legal_moves:
            board.push(move)
            value = max(value, minimax(board, depth-1, alpha, beta, False))
            board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = 9999
        for move in board.legal_moves:
            board.push(move)
            value = min(value, minimax(board, depth-1, alpha, beta, True))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def get_bot_move(level):
    depth = 5 if level=="perfect" else 3
    best_move = None
    best_val = -9999 if board.turn else 9999
    for move in board.legal_moves:
        board.push(move)
        val = minimax(board, depth-1, -10000, 10000, board.turn)
        board.pop()
        if board.turn and val>best_val:
            best_val, best_move = val, move
        if not board.turn and val<best_val:
            best_val, best_move = val, move
    return best_move

def draw():
    canvas.delete("all")
    for r in range(8):
        for c in range(8):
            color = BOARD_COLOR_1 if (r+c)%2==0 else BOARD_COLOR_2
            x1 = c*SQUARE_SIZE + 40
            y1 = r*SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
    files = "abcdefgh"
    ranks = "12345678"
    for i,f in enumerate(files):
        x = i*SQUARE_SIZE+80
        y = 8*SQUARE_SIZE+20
        if flip:
            canvas.create_text(7-i*SQUARE_SIZE//SQUARE_SIZE*0+80, y, text=files[7-i])
        else:
            canvas.create_text(x, y, text=f)
    for i in range(8):
        x = 20
        y = i*SQUARE_SIZE+40
        if flip:
            canvas.create_text(x, y, text=str(i+1))
        else:
            canvas.create_text(x, y, text=str(8-i))
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p and sq != drag_from:
            c = chess.square_file(sq)
            r = chess.square_rank(sq)
            if flip:
                c = 7 - c
                r = 7 - r
            canvas.create_text(c*SQUARE_SIZE+80, (7-r)*SQUARE_SIZE+40, text=p.unicode_symbol(), font=("Arial", 40))
    canvas.create_text(8*SQUARE_SIZE+120, 20, text="PIECE LIBRARY")
    for i,p in enumerate(PIECE_LIBRARY):
        canvas.create_text(8*SQUARE_SIZE+120, 60+i*35, text=p.unicode_symbol(), font=("Arial",30), tags=f"lib_{i}")
    if drag_piece:
        canvas.create_text(drag_x, drag_y, text=drag_piece.unicode_symbol(), font=("Arial",40))
    canvas.create_text(8*SQUARE_SIZE+120, 8*SQUARE_SIZE-20, text="EDIT MODE" if edit_mode else "PLAY MODE", fill="red" if edit_mode else "green")
    root.after(200, check_bot_turn)

def on_down(e):
    global drag_piece, drag_from, drag_x, drag_y
    drag_x, drag_y = e.x, e.y
    for i,p in enumerate(PIECE_LIBRARY):
        if abs(e.x-(8*SQUARE_SIZE+120))<20 and abs(e.y-(60+i*35))<20:
            drag_piece = p
            drag_from = None
            draw()
            return
    c = (e.x-40)//SQUARE_SIZE
    r = 7-(e.y//SQUARE_SIZE)
    if flip:
        c = 7 - c
        r = 7 - r
    if 0<=c<=7 and 0<=r<=7:
        sq = chess.square(c,r)
        p = board.piece_at(sq)
        if p:
            drag_piece = p
            drag_from = sq
            board.remove_piece_at(sq)
            draw()

def on_move(e):
    global drag_x, drag_y
    if drag_piece:
        drag_x, drag_y = e.x, e.y
        draw()

def on_up(e):
    global drag_piece, drag_from
    if not drag_piece:
        return
    c = (e.x-40)//SQUARE_SIZE
    r = 7-(e.y//SQUARE_SIZE)
    if flip:
        c = 7 - c
        r = 7 - r
    if 0<=c<=7 and 0<=r<=7:
        sq = chess.square(c,r)
        board.set_piece_at(sq, drag_piece)
    else:
        if drag_from is not None:
            board.set_piece_at(drag_from, drag_piece)
    drag_piece = None
    drag_from = None
    draw()

def toggle_edit():
    global edit_mode
    edit_mode = not edit_mode
    draw()

def clear_board():
    board.clear()
    draw()

def reset_board():
    board.reset()
    draw()

def flip_board():
    global flip
    flip = not flip
    draw()

def set_white(mode):
    global WHITE_MODE
    WHITE_MODE = mode

def set_black(mode):
    global BLACK_MODE
    BLACK_MODE = mode

def check_bot_turn():
    if board.is_game_over():
        return
    mode = WHITE_MODE if board.turn else BLACK_MODE
    if mode in ("great","perfect"):
        move = get_bot_move(mode)
        if move:
            board.push(move)
            draw()

tk.Button(panel, text="Toggle Edit Mode", command=toggle_edit).pack(fill="x")
tk.Button(panel, text="Reset Board", command=reset_board).pack(fill="x")
tk.Button(panel, text="Clear Board", command=clear_board).pack(fill="x")
tk.Button(panel, text="Flip Board", command=flip_board).pack(fill="x")
tk.Label(panel, text="WHITE BOT").pack(pady=5)
tk.Button(panel, text="Human", command=lambda:set_white("human")).pack(fill="x")
tk.Button(panel, text="Great", command=lambda:set_white("great")).pack(fill="x")
tk.Button(panel, text="Perfect", command=lambda:set_white("perfect")).pack(fill="x")
tk.Label(panel, text="BLACK BOT").pack(pady=5)
tk.Button(panel, text="Human", command=lambda:set_black("human")).pack(fill="x")
tk.Button(panel, text="Great", command=lambda:set_black("great")).pack(fill="x")
tk.Button(panel, text="Perfect", command=lambda:set_black("perfect")).pack(fill="x")

canvas.bind("<ButtonPress-1>", on_down)
canvas.bind("<B1-Motion>", on_move)
canvas.bind("<ButtonRelease-1>", on_up)

draw()
root.mainloop()