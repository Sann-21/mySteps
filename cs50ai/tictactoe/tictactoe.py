"""
Tic Tac Toe Player
"""

import math
import copy
import random
X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    Xcount= 0
    Ocount = 0
    for i in board:
        Xcount+=i.count(X)
        Ocount+=i.count(O)
    if Ocount >= Xcount:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possibleActions = set()

    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == EMPTY:
                possibleActions.add((i, j))

    return possibleActions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    last_move = player(board)

    result_board = copy.deepcopy(board)
    i, j = action

    result_board[i][j] = last_move

    return result_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    if all(i == board[0][0] for i in board[0]):
        return board[0][0]
    elif all(i == board[1][0] for i in board[1]):
        return board[1][0]
    elif all(i == board[2][0] for i in board[2]):
        return board[2][0]
    # Check columns
    elif board[0][0] == board[1][0] and board[1][0] == board[2][0]:
        return board[0][0]
    elif board[0][1] == board[1][1] and board[1][1] == board[2][1]:
        return board[0][1]
    elif board[0][2] == board[1][2] and board[1][2] == board[2][2]:
        return board[0][2]
    # Check diagonals
    elif board[0][0] == board[1][1] and board[1][1] == board[2][2]:
        return board[0][0]
    elif board[0][2] == board[1][1] and board[1][1] == board[2][0]:
        return board[0][2]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) != None:
        return True

    for i in board:
        for j in i:
            if j == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0
    

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if board == initial_state():
        return (random.randint(0, 2), random.randint(0, 2))

    def max_value(board):
        move = ()
        if terminal(board):
            return utility(board), move
        else:
            v = -1
            for action in actions(board):
                minval = min_value(result(board, action))[0]
                if minval >= v:
                    v = minval
                    move = action
            return v, move

    def min_value(board):
        move = ()
        if terminal(board):
            return utility(board), move
        else:
            v = 1
            for action in actions(board):
                maxval = max_value(result(board, action))[0]
                if maxval <= v:
                    v = maxval
                    move = action
            return v, move

    if terminal(board):
        return None

    if player(board) == X:
        return max_value(board)[1]

    else:
        return min_value(board)[1]

