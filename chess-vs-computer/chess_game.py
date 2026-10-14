"""Chess vs Computer. Setup: pip install chess   |   Run: python chess_game.py"""
import math, random, sys
import tkinter as tk
import chess

SZ = 64
FONT = ('Segoe UI Symbol' if sys.platform == 'win32' else
        'Apple Symbols' if sys.platform == 'darwin' else 'DejaVu Sans', 38)
GLY = {chess.PAWN: '♟', chess.KNIGHT: '♞', chess.BISHOP: '♝',
       chess.ROOK: '♜', chess.QUEEN: '♛', chess.KING: '♚'}
VAL = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
       chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}


def evaluate(b, d):
    """Score from White's view: material + small center/pawn-advance bonus."""
    if b.is_checkmate():
        return -(10**5 + d) if b.turn else 10**5 + d
    if b.is_stalemate() or b.is_insufficient_material():
        return 0
    s = 0
    for sq, p in b.piece_map().items():
        f, r = chess.square_file(sq), chess.square_rank(sq)
        v = VAL[p.piece_type]
        if p.piece_type in (chess.PAWN, chess.KNIGHT):
            v += (3.5 - abs(f - 3.5)) * 4 + (3.5 - abs(r - 3.5)) * 4
        if p.piece_type == chess.PAWN:
            v += (r - 1 if p.color else 6 - r) * 5
        s += v if p.color else -v
    return s


def search(b, d, alpha, beta):
    """Minimax with alpha-beta pruning."""
    if d == 0 or b.is_game_over():
        return evaluate(b, d)
    white = b.turn
    ms = sorted(b.legal_moves,
                key=lambda m: -VAL.get(b.piece_type_at(m.to_square) or 0, 0))
    best = -math.inf if white else math.inf
    for m in ms:
        b.push(m)
        v = search(b, d - 1, alpha, beta)
        b.pop()
        if white:
            best = max(best, v); alpha = max(alpha, v)
        else:
            best = min(best, v); beta = min(beta, v)
        if beta <= alpha:
            break
    return best


class App:
    def __init__(s, root):
        s.root = root
        s.side = tk.StringVar(value='White')
        s.lvl = tk.StringVar(value='Medium')
        top = tk.Frame(root); top.pack(pady=6)
        tk.OptionMenu(top, s.side, 'White', 'Black', command=lambda _: s.reset()).pack(side='left')
        tk.OptionMenu(top, s.lvl, 'Easy', 'Medium', 'Hard').pack(side='left')
        tk.Button(top, text='New game', command=s.reset).pack(side='left', padx=4)
        tk.Button(top, text='Undo', command=s.undo).pack(side='left')
        s.st = tk.Label(root, font=('Arial', 12, 'bold')); s.st.pack()
        s.cv = tk.Canvas(root, width=SZ * 8, height=SZ * 8, highlightthickness=0)
        s.cv.pack(padx=8, pady=8)
        s.cv.bind('<Button-1>', s.click)
        s.reset()

    def reset(s):
        s.b = chess.Board()
        s.me = s.side.get() == 'White'
        s.sel, s.hints, s.last, s.busy = None, [], None, False
        s.think() if not s.me else s.draw()

    def sq_at(s, x, y):
        return chess.square(x, 7 - y) if s.me else chess.square(7 - x, y)

    def xy(s, sq):
        f, r = chess.square_file(sq), chess.square_rank(sq)
        return (f, 7 - r) if s.me else (7 - f, r)

    def status(s):
        b = s.b
        if b.is_checkmate():
            return 'Checkmate - ' + ('computer wins' if b.turn == s.me else 'you win!')
        if b.is_game_over():
            return 'Draw'
        if s.busy:
            return 'Computer is thinking...'
        return ('Your move' if b.turn == s.me else 'Computer to move') + (' (check!)' if b.is_check() else '')

    def draw(s):
        c = s.cv; c.delete('all')
        targets = {m.to_square for m in s.hints}
        for sq in chess.SQUARES:
            x, y = s.xy(sq)
            col = '#eeeed2' if (x + y) % 2 == 0 else '#769656'
            if sq == s.sel or (s.last and sq in (s.last.from_square, s.last.to_square)):
                col = '#f6f669'
            c.create_rectangle(x * SZ, y * SZ, (x + 1) * SZ, (y + 1) * SZ, fill=col, width=0)
            cx, cy = x * SZ + SZ // 2, y * SZ + SZ // 2
            p = s.b.piece_at(sq)
            if p:
                fg, sh = ('white', 'black') if p.color else ('black', '#ddd')
                c.create_text(cx + 1, cy + 1, text=GLY[p.piece_type], font=FONT, fill=sh)
                c.create_text(cx, cy, text=GLY[p.piece_type], font=FONT, fill=fg)
            if sq in targets:
                if p:
                    c.create_oval(x * SZ + 4, y * SZ + 4, (x + 1) * SZ - 4, (y + 1) * SZ - 4,
                                  outline='#666', width=4)
                else:
                    c.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill='#666', width=0)
        s.st.config(text=s.status())

    def click(s, e):
        if s.busy or s.b.is_game_over() or s.b.turn != s.me:
            return
        sq = s.sq_at(min(7, e.x // SZ), min(7, e.y // SZ))
        m = next((m for m in s.hints if m.to_square == sq
                  and m.promotion in (None, chess.QUEEN)), None)  # auto-queen
        if m:
            s.b.push(m); s.last = m; s.sel, s.hints = None, []
            return s.think()
        p = s.b.piece_at(sq)
        if p and p.color == s.me:
            s.sel = sq
            s.hints = [m for m in s.b.legal_moves if m.from_square == sq]
        else:
            s.sel, s.hints = None, []
        s.draw()

    def think(s):
        if s.b.is_game_over():
            return s.draw()
        s.busy = True; s.draw()
        s.root.after(50, s.ai)

    def ai(s):
        lv = {'Easy': 0, 'Medium': 2, 'Hard': 3}[s.lvl.get()]
        ms = list(s.b.legal_moves)
        if lv == 0:
            pick = random.choice(ms)
        else:
            random.shuffle(ms)
            white, bv, pick = s.b.turn, None, ms[0]
            for m in ms:
                s.b.push(m)
                v = search(s.b, lv - 1, -math.inf, math.inf)
                s.b.pop()
                if bv is None or (v > bv if white else v < bv):
                    bv, pick = v, m
        s.b.push(pick); s.last = pick; s.busy = False
        s.draw()

    def undo(s):
        if s.busy:
            return
        if s.b.move_stack: s.b.pop()
        if s.b.turn != s.me and s.b.move_stack: s.b.pop()
        s.sel, s.hints, s.last = None, [], None
        s.think() if s.b.turn != s.me else s.draw()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Chess vs Computer')
    root.resizable(False, False)
    App(root)
    root.mainloop()
