import chess
import tkinter as tk

SQUARE_SIZE = 80
BOARD_COLOR_1 = "#F0D9B5"
BOARD_COLOR_2 = "#B58863"
HIGHLIGHT = "#FFD54F"

board = chess.Board()
edit_mode = False

drag_piece = None
drag_from = None
drag_x = drag_y = 0

selected_square = None

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
root.title("Chess Sandbox")

canvas = tk.Canvas(root, width=8*SQUARE_SIZE+200, height=8*SQUARE_SIZE+40)
canvas.pack()

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
    for i,f in enumerate("abcdefgh"):
        canvas.create_text(i*SQUARE_SIZE+80, 8*SQUARE_SIZE+20, text=f)
    for i in range(8):
        canvas.create_text(20, i*SQUARE_SIZE+40, text=str(8-i))
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p and sq != drag_from:
            c = chess.square_file(sq)
            r = 7 - chess.square_rank(sq)
            canvas.create_text(c*SQUARE_SIZE+80, r*SQUARE_SIZE+40, text=p.unicode_symbol(), font=("Arial", 40))
    canvas.create_text(8*SQUARE_SIZE+120, 20, text="PIECE LIBRARY")
    for i,p in enumerate(PIECE_LIBRARY):
        canvas.create_text(8*SQUARE_SIZE+120, 60 + i*35, text=p.unicode_symbol(), font=("Arial", 30), tags=f"lib_{i}")
    if drag_piece:
        canvas.create_text(drag_x, drag_y, text=drag_piece.unicode_symbol(), font=("Arial", 40))
    canvas.create_text(8*SQUARE_SIZE+120, 8*SQUARE_SIZE-20, text="EDIT MODE" if edit_mode else "PLAY MODE", fill="red" if edit_mode else "green")

def on_down(e):
    global drag_piece, drag_from, drag_x, drag_y
    drag_x, drag_y = e.x, e.y
    for i,p in enumerate(PIECE_LIBRARY):
        if abs(e.x-(8*SQUARE_SIZE+120)) < 20 and abs(e.y-(60+i*35)) < 20:
            drag_piece = p
            drag_from = None
            draw()
            return
    c = (e.x-40)//SQUARE_SIZE
    r = 7 - (e.y//SQUARE_SIZE)
    if 0 <= c <= 7 and 0 <= r <= 7:
        sq = chess.square(c, r)
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
    r = 7 - (e.y//SQUARE_SIZE)
    if 0 <= c <= 7 and 0 <= r <= 7:
        sq = chess.square(c, r)
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

tk.Button(root, text="Toggle Edit Mode", command=toggle_edit).pack()
tk.Button(root, text="Reset Board", command=reset_board).pack()
tk.Button(root, text="Clear Board", command=clear_board).pack()

canvas.bind("<ButtonPress-1>", on_down)
canvas.bind("<B1-Motion>", on_move)
canvas.bind("<ButtonRelease-1>", on_up)

draw()
root.mainloop()