import chess
import chess.pgn
from pathlib import Path
import requests, sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import heapq, time, shutil


# repertoire = "W1 - Fast Developing Center-White"
repertoire = sys.argv[1]

# class MyVisitor(chess.pgn.GameBuilder):
#     def visit_header(self, tagname, tagvalue):
#         if tagname == "WhiteElo":
#             self.white = tagvalue
#         elif tagname == "BlackElo":
#             self.black = tagvalue
#         self.movenum = 0

#     def visit_move(self, board, move):

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = 1.0
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)

http = requests.Session()

retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
http.mount("https://", TimeoutHTTPAdapter(timeout=1.0, max_retries=retries))


def encode_fen(fen):
    if fen is None:
        return None
    new_fen = fen.split()
    new_fen = new_fen[:-2]
    new_fen = " ".join(new_fen)
    return new_fen



def decode_prob(prob):
    return 1.0 - prob
    
def encode_prob(prob):
    return 1.0 - prob

def extract_prob(tuple_entry):
    return decode_prob(tuple_entry[0])

def extract_fen(tuple_entry):
    return tuple_entry[1]

def extract_move(tuple_entry):
    return tuple_entry[2]

def get_fen_prob(fen):
    if fen is None:
        return 1.0
    return decode_prob(fen_probs[encode_fen(fen)])

def get_board_fen(board):
    return encode_fen(board.fen())

is_white = "White" in repertoire

need_moves = []

have_moves = {}

pos_heap = []

mov_parents = {}

fen_probs = {encode_fen(chess.STARTING_FEN): 0.0}

db_url = "https://explorer.lichess.ovh/lichess?variant=standard&speeds[]=blitz&ratings[]=1600&fen={}"

def get_tot(pos_dict):
    tot = 0
    tot += pos_dict["white"]
    tot += pos_dict["draws"]
    tot += pos_dict["black"]
    return tot

def do_move(board):
    board_fen = get_board_fen(board)
    # print(have_moves)
    # print(board_fen)
    if board_fen not in have_moves:
        return None
    print(have_moves[board_fen])
    board.push_san(have_moves[board_fen])
    return board

def recurse_pos(board):
    if is_white:
        board = do_move(board)

    print(board.fen())
    res = http.get(db_url.format(board.fen()))
    time.sleep(0.1)
    res_dict = res.json()
    # print(res_dict)
    moves = res_dict["moves"]
    pos_tot = get_tot(res_dict)

    encoded_fen = encode_fen(board.fen())



    for move in moves:
        # print(move["san"])
        tot = get_tot(move)
        odds = tot / pos_tot
        try:
            mv = board.pop()
            old_fen = board.fen()
            board.push(mv)
            add_pos(old_fen, board.fen(), move["san"], odds)
        except IndexError:
            add_pos(None, board.fen(), move["san"], odds)
    
    # print(len(need_moves))

    if len(need_moves) < 5 and len(pos_heap) < 10000:
        newboard = None
        while len(pos_heap) > 0 and newboard is None:
            popped = pop_pos()
            newboard = chess.Board(popped[1])
            fen = get_board_fen(newboard)
            if fen not in have_moves:
                need_moves.append((get_fen_prob(newboard.fen()), fen, popped[2]))
                newboard = None
            elif not is_white:
                newboard = do_move(newboard)
        if newboard is not None:
            recurse_pos(newboard)


def add_pos(old_fen, fen, move, rel_prob):
    base_prob = get_fen_prob(old_fen)

    

    pos_board = chess.Board(fen)

    # print(pos_board)
    # print()

    resulting_board = pos_board.push_san(move)

    # print(pos_board)
    # print("--------")

    resulting_fen = encode_fen(pos_board.fen())

    # if old_fen is not None:
    mov_parents[resulting_fen] = (encode_fen(old_fen),move)



    pos_prob = base_prob * rel_prob

    pos_to_push = (encode_prob(pos_prob), resulting_fen, move)

    if resulting_fen not in fen_probs:
        fen_probs[resulting_fen] = 0
    else:
        ind = 0
        found_pos = None
        for pos in pos_heap:
            if extract_fen(pos) == resulting_fen:
                pos_heap.remove(pos)
                heapq.heapify(pos_heap)
                found_pos = pos
            ind += 1
        if found_pos != None:
            found_prob = extract_prob(found_pos)
            pos_prob = found_prob + pos_prob
            pos_to_push = (encode_prob(pos_prob), found_pos[1], found_pos[2])
            # found_pos[0] = encode_prob(pos_prob)
            # pos_to_push = found_pos

    fen_probs[resulting_fen] = encode_prob(pos_prob)

    heapq.heappush(pos_heap, pos_to_push)

def pop_pos():
    # print(pos_heap)
    # print()
    # print()
    return heapq.heappop(pos_heap)

def load_pgn():
    gaem = chess.pgn.read_game(trypgn)
    nodes = [gaem]  
    if is_white:
        node = nodes.pop()
        node_fen = encode_fen(node.board().fen())
        have_moves[node_fen] = node.board().san(node.variations[0].move)
        nodes.append(node.variations[0])
    while len(nodes) > 0:
        parent = nodes.pop()
        for node in parent.variations:
            if not node.is_end():
                nodes.append(node.variations[0])
                node_fen = encode_fen(node.board().fen())
                # print(node.variations[0])
                if node_fen not in have_moves:
                    have_moves[node_fen] = node.board().san(node.variations[0].move)

game_num = 0

to_dir = Path.cwd() / "build" / "todo"

if to_dir.exists():
    shutil.rmtree(to_dir)

to_dir.mkdir()



def build_pgn(fen):
    # print(fen)
    moves = []
    while fen is not None:
        if fen in mov_parents:
            parent = mov_parents[fen]
            fen = parent[0]
            mov = parent[1]
            moves.append(mov)
        else:
            fen = None
        if fen is not None:
            moves.append(have_moves[fen])
    pgn_board = chess.Board()
    while len(moves) > 0:
        pgn_board.push_san(moves.pop())
    pgn_file = to_dir / ("Opening{}.pgn".format(game_num))
    print(chess.pgn.Game.from_board(pgn_board), file=pgn_file.open("w"), end="\n\n")
    

heapq.heapify(pos_heap)

with open(Path.cwd() / "resources" / (repertoire + ".pgn"), "r") as trypgn:
    # chess.pgn.read_game(trypgn, Visitor=MyVisitor)
    newboard = chess.Board()
    # gaem = chess.pgn.read_game(trypgn)

    # for move in first_game.mainline_moves():
    #     board.push(move)
    # for variation in gaem.variations:
    load_pgn()
    # print(have_moves)
    recurse_pos(newboard)
    # raise
    # print(gaem.variations[1])
for i in range(0, len(need_moves)):
    print(need_moves[i][0])
    build_pgn(need_moves[i][1])
    game_num += 1
# print(have_moves)
# print(len(need_moves))
# print(need_moves)
# print(mov_parents[need_moves[0][1]])
# print(mov_parents[need_moves[1][1]])
# print(mov_parents[need_moves[2][1]])
# print(mov_parents[need_moves[3][1]])
# print(mov_parents[need_moves[4][1]])
# print(mov_parents[need_moves[5][1]])
# build_pgn(need_moves[6][1])


