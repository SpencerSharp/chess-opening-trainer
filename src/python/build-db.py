import chess
import chess.pgn
import bz2
from pathlib import Path
import shutil
import time

fil = Path.cwd() / "resources" / "2020-06.pgn.bz2"

fen_dir = Path.cwd() / "build" / "positions"

# if fen_dir.exists():
#     shutil.rmtree(fen_dir)

# print("Old has been deleted")

# fen_dir.mkdir()

def encode_fen(fen):
    return fen.replace("/",":")

def decode_fen(fen):
    return fen.replace(":",":")

def get_hash_dir(board):

    hash_dir = fen_dir
    # if board.turn is chess.WHITE:
    #     hash_dir = hash_dir / "W"
    # elif board.turn is chess.BLACK:
    #     hash_dir = hash_dir / "B"
    # else:
    #     hash_dir = hash_dir / "X"
    
    # if board.has_castling_rights(chess.WHITE):
    #     hash_dir = hash_dir / "Y"
    # else:
    #     hash_dir = hash_dir / "N"
    
    # if board.has_castling_rights(chess.BLACK):
    #     hash_dir = hash_dir / "Y"
    # else:
    #     hash_dir = hash_dir / "N"
    
    # if board.has_legal_en_passant():
    #     hash_dir = hash_dir / "Y"
    # else:
    #     hash_dir = hash_dir / "N"

    # for i in (1, 6):
    #     for j in range(1,7):
    #         piece_name = board.piece_at(chess.square(i, j))
    #         if piece_name == None:
    #             piece_name = "X"
    #         else:
    #             if piece_name.piece_type == chess.PAWN:
    #                 piece_name = "P"
    #             else:
    #                 piece_name = "O"
    #         hash_dir = hash_dir / piece_name

    if not hash_dir.exists():
        hash_dir.mkdir(parents=True)
    
    hash_fil = hash_dir / "games"

    hash_fil.touch()
    
    return hash_fil


class MyVisitor(chess.pgn.GameBuilder):
    def visit_header(self, tagname, tagvalue):
        if tagname == "WhiteElo":
            self.white = tagvalue
        elif tagname == "BlackElo":
            self.black = tagvalue
        self.movenum = 0

    def visit_move(self, board, move):
        if self.movenum > 15:
            return
        board.halfmove_clock = 0
        board.fullmove_number = 0
        encoded_fen = encode_fen(board.fen())
        fen_path = get_hash_dir(board)
        with open(fen_path, "a") as fen_fil:
            # fen_fil.write(encoded_fen)
            # fen_fil.write(" ")
            ln = move.uci()
            # if board.turn is chess.WHITE:
            #     fen_fil.write(self.white)
            # elif board.turn is chess.BLACK:
            #     fen_fil.write(self.black)
            # fen_fil.write(" ")
            fen_fil.write(ln)
            fen_fil.write("\n")
        self.movenum += 1

maxpos_fil = Path.cwd() / "build" / "maxpos.txt"

BATCH_SIZE = 10000000
maxpos = int(maxpos_fil.read_text())
count = 0

with bz2.open(fil, 'rt') as trypgn:
    try:
        while True:
            # if count < maxpos:
                # chess.pgn.read_game(trypgn)
            # else:
            chess.pgn.read_game(trypgn, Visitor=MyVisitor)
                # maxpos_fil.write_text(str(count))
            count += 1
            if count % 1000 == 0:
                print(count)
            # time.sleep(0.01)
            if (count > (maxpos + BATCH_SIZE)):
                break
    except:
        print("error")
    # # print(first_game)


