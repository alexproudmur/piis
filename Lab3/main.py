import chess
import chess.engine
import time
import chess.svg

# from IPython.display import SVG, display

engine = chess.engine.SimpleEngine.popen_uci("stockfish_15_win_x64_avx2/stockfish_15_x64_avx2.exe")


def stockfish_eval(board_instance, is_max):
    info = engine.analyse(board_instance, chess.engine.Limit(depth=1))
    score = info['score']

    if not is_max:
        result = chess.engine.PovScore(score, chess.BLACK).pov(chess.BLACK).relative.score()
    else:
        result = chess.engine.PovScore(score, chess.WHITE).pov(chess.WHITE).relative.score()
    if result is None:
        result = 0
    return result


def best_move_nega_max(board_instance, depth):
    def nega_max(board, depth, is_max):
        if depth == 0:
            return stockfish_eval(board, is_max)

        max_value_in = -1_000_000
        for legal_move in board.legal_moves:
            move = chess.Move.from_uci(str(legal_move))
            boardCopy = board.copy()
            boardCopy.push(move)
            value = -nega_max(boardCopy, depth - 1, 1 - is_max)
            if value > max_value_in:
                max_value_in = value
        return max_value_in

    max_value = -1_000_000
    best_move = None
    for legal_move in board_instance.legal_moves:
        move = chess.Move.from_uci(str(legal_move))
        board_copy = board_instance.copy()
        board_copy.push(move)
        value = -nega_max(board_copy, depth, 1 - board_copy.turn)
        if value > max_value:
            max_value = value
            best_move = move
    return best_move


def best_move_nega_scout(board_instance, depth, alpha=-999999, beta=999999):
    def nega_scout(board, depth_in, alpha_in, beta_in):
        if depth_in == 0:
            return stockfish_eval(board, board.turn)
        score_in = -1_000_000
        n = beta_in
        for legal_move in board.legal_moves:
            move = chess.Move.from_uci(str(legal_move))
            board_copy = board.copy()
            board_copy.push(move)
            current = -nega_scout(board_copy, depth_in - 1, -n, -alpha_in)
            if current > score_in:
                if n == beta or depth_in <= 2:
                    score_in = current
                else:
                    score_in = -nega_scout(board_copy, depth_in - 1, -beta_in, -current)
            if score_in > alpha_in:
                alpha_in = score_in
            if alpha_in >= beta_in:
                return alpha_in
            n = alpha_in + 1
        return score_in

    score = -1_000_000
    best_move = None
    for legal_move in board_instance.legal_moves:
        move = chess.Move.from_uci(str(legal_move))
        board_copy = board_instance.copy()
        board_copy.push(move)
        value = -nega_scout(board_copy, depth, alpha, beta)
        if value > score:
            score = value
            best_move = move

    return best_move


def best_move_pvs(board_instance, depth, alpha=-999999, beta=999999):
    def pvs(board, depth_in, alpha_in, beta_in):
        if depth_in == 0:
            return stockfish_eval(board, board.turn)
        b_search_pv_in = True
        for legal_move in board.legal_moves:
            move = chess.Move.from_uci(str(legal_move))
            board_copy = board.copy()
            board_copy.push(move)
            if b_search_pv_in:
                current = -pvs(board_copy, depth_in - 1, -beta_in, -alpha_in)
            else:
                current = -pvs(board_copy, depth_in - 1, -alpha_in - 1, -alpha_in)
                if alpha_in < current < beta_in:
                    current = -pvs(board_copy, depth_in - 1, -beta_in, -alpha_in)
            if current >= beta_in:
                return beta_in
            if current > alpha_in:
                alpha_in = current
                b_search_pv_in = False

        return alpha_in

    score = -1_000_000
    best_move = None
    for legal_move in board_instance.legal_moves:
        move = chess.Move.from_uci(str(legal_move))
        board_copy = board_instance.copy()
        board_copy.push(move)
        value = -pvs(board_copy, depth, alpha, beta)
        if value > score:
            score = value
            best_move = move

    return best_move


def game_pvs(depth=1):
    board = chess.Board()
    n = 0

    while board.is_checkmate() != True and board.is_fivefold_repetition() != True and board.is_seventyfive_moves() != True:
        start = time.time()
        if n % 2 == 0:
            print("White Turn")
            move = best_move_pvs(board, depth)
        else:

            print("Black Turn")
            move = best_move_pvs(board, depth)
        end = time.time()

        if move is None:
            print("GG, checkmate")
            break

        print("Move in UCI format:", move)
        print("Time taken by Move:", end - start)
        print("Moves taken:", n)
        print("FiveFold", board.is_fivefold_repetition())

        board.push(move)
        # display(SVG(chess.svg.board(board, size=400)))
        print(board)
        print("\n")
        n = n + 1
    if board.is_fivefold_repetition():
        print("GG, fivefold")


def game_nega_scout(depth=1):
    board = chess.Board()
    n = 0

    while board.is_checkmate() != True and board.is_fivefold_repetition() != True and board.is_seventyfive_moves() != True:
        start = time.time()
        if n % 2 == 0:
            print("White Turn")
            move = best_move_nega_scout(board, depth)
        else:

            print("Black Turn")
            move = best_move_nega_scout(board, depth)
        end = time.time()

        if move is None:
            print("GG, checkmate")
            break

        print("Move in UCI format:", move)
        print("Time taken by Move:", end - start)
        print("Moves taken:", n)
        print("FiveFold", board.is_fivefold_repetition())

        board.push(move)
        # display(SVG(chess.svg.board(board, size=400)))
        print(board)
        print("\n")
        n = n + 1
    if board.is_fivefold_repetition():
        print("GG, fivefold")


def game_nega_max(depth=1):
    board = chess.Board()
    n = 0

    while board.is_checkmate() != True and board.is_fivefold_repetition() != True and board.is_seventyfive_moves() != True:
        start = time.time()
        if n % 2 == 0:
            print("White Turn")
            move = best_move_nega_max(board, depth)
        else:

            print("Black Turn")
            move = best_move_nega_max(board, depth)
        end = time.time()

        if move is None:
            print("Checkmate")
            break

        print("Move in UCI format:", move)
        print("Time taken by Move:", end - start)
        print("Moves taken:", n)
        print("FiveFold", board.is_fivefold_repetition())

        board.push(move)
        # display(SVG(chess.svg.board(board, size=400)))
        print(board)
        print("\n")
        n = n + 1
    if board.is_fivefold_repetition():
        print("Fivefold")


if __name__ == '__main__':
    # invoke game func
    game_pvs()
    engine.quit()
