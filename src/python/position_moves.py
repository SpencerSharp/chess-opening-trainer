import chess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import scipy.stats as stats
import math

fen_dir = Path.cwd() / "build" / "positions"

def get_hash_dir(board):
    hash_dir = fen_dir
    if board.turn is chess.WHITE:
        hash_dir = hash_dir / "W"
    elif board.turn is chess.BLACK:
        hash_dir = hash_dir / "B"
    else:
        hash_dir = hash_dir / "X"
    
    if board.has_castling_rights(chess.WHITE):
        hash_dir = hash_dir / "Y"
    else:
        hash_dir = hash_dir / "N"
    
    if board.has_castling_rights(chess.BLACK):
        hash_dir = hash_dir / "Y"
    else:
        hash_dir = hash_dir / "N"
    
    if board.has_legal_en_passant():
        hash_dir = hash_dir / "Y"
    else:
        hash_dir = hash_dir / "N"

    for i in (1, 6):
        for j in range(1,7):
            piece_name = board.piece_at(chess.square(i, j))
            if piece_name == None:
                piece_name = "X"
            else:
                if piece_name.piece_type == chess.PAWN:
                    piece_name = "P"
                else:
                    piece_name = "O"
            hash_dir = hash_dir / piece_name

    if not hash_dir.exists():
        hash_dir.mkdir(parents=True)
    
    hash_fil = hash_dir / "games"

    hash_fil.touch()
    
    return hash_fil

def encode_fen(fen):
    return fen.replace("/",":")

def decode_fen(fen):
    return fen.replace(":",":")

fen = "r1bqkbnr/ppp1pppp/2n5/3p4/4P3/2N5/PPPP1PPP/R1BQKBNR w KQkq - 0 0"

board = chess.Board(fen=fen)

enc_fen = encode_fen(fen)

hash_fil = get_hash_dir(board)

mvs = {}

with hash_fil.open() as moves:
    while True:
        ln = moves.readline()
        fields = ln.split()

        if len(fields) < 2:
            break

        move = fields[len(fields)-1]
        elo = fields[len(fields)-2]

        cur_fen = " ".join(fields[0:len(fields)-2])

        if enc_fen != cur_fen:
            continue

        if move not in mvs:
            mvs[move] = [elo]
        else:
            mvs[move].append(elo)

MY_ELO = 1100
STDEV_EST = 50
MAX_WEIGHT = stats.norm.pdf(MY_ELO, MY_ELO, STDEV_EST)

def create_and_show_dist():
    mine = plt.figure()
    mu = MY_ELO
    sigma = STDEV_EST
    x = np.linspace(800, 1400, 400)
    mfa = stats.norm.pdf(x,loc=mu,scale=sigma)
    plt.plot(x, mfa)
    plt.ylim(bottom=0)

    mine.savefig(Path.cwd() / 'weiaHAHAboomsik.png')


def get_weight(elo):
    return MAX_WEIGHT * stats.norm.pdf(int(elo),loc=MY_ELO,scale=STDEV_EST)

def fnc(listtt):
    tot = 0
    for guy in listtt:
        tot += get_weight(guy)
    return tot

def get_moves():
    srs = pd.Series(mvs)
    cpr = srs.apply(fnc)
    cpr.sort_values(ascending=False,inplace=True)

    return cpr

print(get_moves())

create_and_show_dist()
# print(get_weight(1100))

