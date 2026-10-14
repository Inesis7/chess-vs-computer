# Chess vs Computer

Play chess against a computer opponent. Same engine idea in three versions.

| Version | File | Run it |
|---|---|---|
| Desktop (tkinter) | `chess_game.py` | `pip install -r requirements.txt` then `python chess_game.py` |
| Browser | `web/index.html` | Open the file in a browser (needs internet for chess.js) |
| Google Colab | `chess_colab.ipynb` | Upload to Colab, Run all, type moves like `e2e4` |

## How the computer plays
- Minimax search with alpha-beta pruning
- Evaluation: material + small bonus for center control and pawn advancement
- Levels: Easy (random), Medium (2 moves deep), Hard (3 moves deep)

## Limits
- Pawn promotion is always a queen in the desktop and browser versions
- No opening book or deep strategy, so Hard is decent but not strong

## Ideas to improve
- Piece-square tables, iterative deepening, move ordering
- Move history panel, captured pieces display
