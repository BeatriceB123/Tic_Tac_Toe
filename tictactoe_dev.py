import random
import numpy as np
import pygame
import sys
import time
from pygame.locals import *

WINDOWWIDTH = 720  # size of window's width in pixels
WINDOWHEIGHT = 720  # size of windows' height in pixels
BOXSIZE = 200  # size of box height & width in pixels
MARGIN = 60  # size of gap between boxes in pixels
LINE_WIDTH = 7  # For odd width values, the thickness of each line grows with the original line being in the cent
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
oo = 6000

#                 #  R    G    B
BACKGROUND_COLOR = (153, 255, 153)
LINE_COLOR = (0, 0, 255)
HIGHLIGHTCOLOR = (60, 60, 100)
player1_image = pygame.image.load("emoji1.png")
player2_image = pygame.image.load("emoji2.png")

dict_image_coordinates = dict(
    [((i, j), (MARGIN + j * BOXSIZE, MARGIN + i * BOXSIZE)) for i in range(3) for j in range(3)])

positions_to_analize = [
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(2, 0), (1, 1), (0, 2)]]


class ProblemState:
    # -1 va fi calculatorul, +1 va fi omul
    def __init__(self):
        self.square = np.zeros((3, 3))
        self.moves_next = 1

    def __eq__(self, other):
        return self.moves_next == other.moves_next

    def __str__(self):
        res = ""
        for i in self.square:
            res += str([str(int(j)) if j >= 0 else '-' for j in i]) + '\n'
        res += "Next: " + str(self.moves_next)
        return res


def copy_state(state):
    other = ProblemState()
    other.square = np.array(state.square, copy=True)
    other.moves_next = state.moves_next
    return other


def display_board():
    pygame.init()
    pygame.display.set_caption('TIC-TAC-TOE')
    DISPLAYSURF.fill(BACKGROUND_COLOR)
    for line in range(0, 3 * BOXSIZE + 1, BOXSIZE):
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (MARGIN + line, MARGIN), (MARGIN + line, MARGIN + 3 * BOXSIZE),
                         LINE_WIDTH)
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (MARGIN, MARGIN + line), (MARGIN + 3 * BOXSIZE, MARGIN + line),
                         LINE_WIDTH)


def update_board(state):
    for i in range(3):
        for j in range(3):
            coordx, coordy = dict_image_coordinates[(i, j)]
            coordx += LINE_WIDTH
            coordy += LINE_WIDTH
            if state.square[i][j] == 1:
                DISPLAYSURF.blit(player1_image, (coordx, coordy))
            elif state.square[i][j] == -1:
                DISPLAYSURF.blit(player2_image, (coordx, coordy))


def print_final_message(win):
    pygame.time.wait(1_000)
    DISPLAYSURF.fill(BACKGROUND_COLOR)
    font = pygame.font.SysFont("comicsansms", 72)
    str_message = "Equality"
    if win == 1:
        str_message = "Player win"
    elif win == -1:
        str_message = "AI win"
    text = font.render(str_message, True, (0, 128, 0))
    DISPLAYSURF.blit(text, (350 - text.get_width() // 2, 250 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(1_000)


def is_final_state(state):
    if who_completed_a_line(state) != 0:
        return True  # someone managed to make a complete line
    if 0 not in state.square:
        return True  # filled up
    return False


def who_completed_a_line(state):
    for li in positions_to_analize:
        if state.square[li[0][0]][li[0][1]] == state.square[li[1][0]][li[1][1]] == state.square[li[2][0]][li[2][1]] and \
                state.square[li[0][0]][li[0][1]] != 0:
            return state.square[li[0][0]][li[0][1]]
    return 0


def is_valid_transition(state, pozi, pozj):
    if (pozi not in range(3)) or (pozj not in range(3)):
        return False
    if state.square[pozi][pozj] != 0:
        return False
    return True


def make_transition(state, pozi, pozj):
    new_state = copy_state(state)
    new_state.square[pozi, pozj] = state.moves_next
    new_state.moves_next = -state.moves_next
    return new_state


# primeste evenimentul - pe ce s-a apasat, si returneaza din ce careu face parte piesa
def determine_coordinates_box(e):
    x, y = e
    cari = carj = 3

    if x and y in range(MARGIN, MARGIN + 3 * BOXSIZE + 1):  # in square
        for k in range(3, 0, -1):
            if e[0] < MARGIN + k * BOXSIZE:
                x = MARGIN + (k - 1) * BOXSIZE
                carj = k - 1  # daca e pe linia
            if e[1] < MARGIN + k * BOXSIZE:
                y = MARGIN + (k - 1) * BOXSIZE
                cari = k - 1
        return x + LINE_WIDTH, y + LINE_WIDTH, cari, carj
    return None, None, None, None


def process_the_event(state, e):
    coordx, coordy, i, j = determine_coordinates_box(e)
    if any([coordx, coordy, i, j]):
        if is_valid_transition(state, i, j):
            state = make_transition(state, i, j)
    return state


def computer_moves_random(state):
    while state.moves_next == -1:
        computer_coord = np.random.choice(range(3), 2, p=np.ones(3).dot(1 / 3))
        if is_valid_transition(state, *computer_coord):
            state = make_transition(state, *computer_coord)
    return state


def get_state_score_naive(state, previous_state):
    score = 0
    for li in positions_to_analize:
        # avem deja 3 intr-o linie
        if state.square[li[0][0]][li[0][1]] == state.square[li[1][0]][li[1][1]] == state.square[li[2][0]][
            li[2][1]] != 0:
            return 100
        if state.square[li[0][0]][li[0][1]] == state.square[li[1][0]][li[1][1]] == 1 \
                and state.square[li[2][0]][li[2][1]] == -1 and previous_state.square[li[2][0]][li[2][1]] == 0:
            return 50
        if state.square[li[2][0]][li[2][1]] == state.square[li[1][0]][li[1][1]] == 1 \
                and state.square[li[0][0]][li[0][1]] == -1 and previous_state.square[li[0][0]][li[0][1]] == 0:
            return 50
        if state.square[li[0][0]][li[0][1]] == state.square[li[2][0]][li[2][1]] == 1 \
                and state.square[li[1][0]][li[1][1]] == -1 and previous_state.square[li[1][0]][li[1][1]] == 0:
            return 50
        # avem 2 piese de culoarea noastra care nu au nimic intre ele (inca mai putem folosi aceasta linie)
        elif state.square[li[0][0]][li[0][1]] == state.square[li[1][0]][li[1][1]] and state.square[li[1][0]][
            li[1][1]] != 0:
            if state.square[li[2][0]][li[2][1]] == 0:
                score -= 5 * state.square[li[0][0]][li[0][1]]
        elif state.square[li[1][0]][li[1][1]] == state.square[li[2][0]][li[2][1]] and state.square[li[1][0]][
            li[1][1]] != 0:
            if state.square[li[0][0]][li[0][1]] == 0:
                score -= 5 * state.square[li[1][0]][li[1][1]]
        elif state.square[li[0][0]][li[0][1]] == state.square[li[2][0]][li[2][1]] and state.square[li[0][0]][
            li[0][1]] != 0:
            if state.square[li[1][0]][li[1][1]] == 0:
                score -= 5 * state.square[li[2][0]][li[2][1]]
        # avem o pozitie deschisa cu o singura piesa pusa
        elif state.square[li[0][0]][li[0][1]] != 0 and state.square[li[1][0]][li[1][1]] == state.square[li[2][0]][
            li[2][1]] == 0:
            score -= 2 * state.square[li[0][0]][li[0][1]]
        elif state.square[li[1][0]][li[1][1]] != 0 and state.square[li[0][0]][li[0][1]] == state.square[li[2][0]][
            li[2][1]] == 0:
            score -= 2 * state.square[li[1][0]][li[1][1]]
        elif state.square[li[2][0]][li[2][1]] != 0 and state.square[li[0][0]][li[0][1]] == state.square[li[1][0]][
            li[1][1]] == 0:
            score -= 2 * state.square[li[2][0]][li[2][1]]
    return score


def computer_moves_based_on_one_level_results(state):
    li = []  # list of possible states, with maximum scores
    max_score = -oo
    for i in range(3):
        for j in range(3):
            if state.square[i][j] == 0:  # free space
                if is_valid_transition(state, i, j):
                    new_state = make_transition(state, i, j)
                    new_score = get_state_score_naive(new_state, state)
                    if new_score == max_score:
                        li.append((new_state, new_score, i, j))
                    elif new_score > max_score:
                        li = [(new_state, new_score, i, j)]
                        max_score = new_score
    chosed_move = random.choice(li)
    print("Mutare Aleasa: ", chosed_move)
    state = make_transition(state, chosed_move[2], chosed_move[3])
    return state


def play(state):
    display_board()
    while True:
        if is_final_state(state):
            print_final_message(who_completed_a_line(state))
            break
        if state.moves_next == 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    state = process_the_event(state, event.pos)
                    # print(get_state_score_naive(state))
        elif state.moves_next == -1:
            start_time = time.time()
            # state = computer_moves_based_on_one_level_results(state)
            state = minimax(state, 3, 3)
            # state = minimax_alphabeta(state, 3, 3)  # asta e pt incercarea #1
            # result = minimax_alphabeta(state)
            # state = make_transition(state, result[1], result[2])
            # print(get_state_score_naive(state))
            print("The running time is:", time.time() - start_time)

        update_board(state)
        pygame.display.update()


def minimax(state, max_depth, depth=2, mode="max"):
    if depth == max_depth and mode == "max":
        victory_check = computer_moves_based_on_one_level_results(state)
        if get_state_score_naive(victory_check, state) in (50, 100):
            return victory_check
    scores = []
    for i in range(3):
        for j in range(3):
            if state.square[i][j] == 0:
                aux_state = make_transition(state, i, j)
                if mode == "max":
                    aux_score = minimax(aux_state, max_depth, depth, "min")
                elif mode == "min" and depth > 1:
                    aux_score = minimax(aux_state, max_depth, depth - 1, "max")
                else:
                    aux_score = get_state_score_naive(aux_state, state)
                if aux_score is not None:
                    scores.append((aux_score, i, j))
    # print(mode, depth, scores)
    if mode == "max" and depth == max_depth:
        best_result = max(scores, key=lambda x: x[0])
        scores = list(filter(lambda x: x[0] == best_result[0], scores))
        best_result = random.choice(scores)
        if best_result[0] != -oo:
            best_state = make_transition(state, best_result[1], best_result[2])
        else:
            best_state = computer_moves_based_on_one_level_results(state)
        return best_state
    elif mode == "max":
        if len(scores) > 0:
            best_result = max(scores, key=lambda x: x[0])
            return best_result[0]
        else:
            return -oo
    else:
        best_result = min(scores, key=lambda x: x[0])
        return best_result[0]


def minimax_alphabeta(state, max_depth, depth=2, mode="max", alpha=-oo, beta=oo):
    # if depth == 2 and mode == "max":
    #     for i in range(0, 3):
    #         for j in range(0, 3):
    #             if state.square[i][j] == 0:
    #                 victory_check = make_transition(state, i, j)
    #                 if get_state_score_naive(victory_check) == 100:
    #                     return 100, i, j
    # if is_final_state(state) or (depth == 1 and mode == "min"):
    #     return get_state_score_naive(state), -1, -1
    # if mode == "max":
    #     value = (-oo, -1, -1)
    #     i, stop = 0, False
    #     while i < 3 and not stop:
    #         j = 0
    #         while j < 3 and not stop:
    #             if state.square[i][j] == 0:
    #                 aux_state = make_transition(state, i, j)
    #                 aux_value = minimax_alphabeta(aux_state, depth, "min", alpha, beta)
    #                 value = (max(value[0], aux_value[0]), i, j)
    #                 alpha = max(alpha, value[0])
    #                 if alpha >= beta:
    #                     stop = True
    #             j += 1
    #         i += 1
    #     return value
    # if mode == "min":
    #     value = (oo, -1, -1)
    #     i, stop = 0, False
    #     while i < 3 and not stop:
    #         j = 0
    #         while j < 3 and not stop:
    #             if state.square[i][j] == 0:
    #                 aux_state = make_transition(state, i, j)
    #                 aux_value = minimax_alphabeta(aux_state, depth - 1, "max", alpha, beta)
    #                 value = (min(value[0], aux_value[0]), i, j)
    #                 beta = min(beta, value[0])
    #                 if alpha >= beta:
    #                     stop = True
    #             j += 1
    #         i += 1
    #     return value

    # incercarea #1
    if depth == max_depth and mode == "max":
        prevent_victory = None
        victory_check = computer_moves_based_on_one_level_results(state)
        if get_state_score_naive(victory_check, state) in (50, 100):
            return victory_check
    scores = []
    if mode == "max":
        aux_score = -oo
    else:
        aux_score = oo
    i, stop = 0, False
    while i < 3 and not stop:
        j = 0
        while j < 3 and not stop:
            if state.square[i][j] == 0:
                aux_state = make_transition(state, i, j)
                if mode == "max":
                    aux_score = max(aux_score, minimax_alphabeta(aux_state, max_depth, depth, "min", alpha, beta))
                    alpha = max(alpha, aux_score)
                    if alpha >= beta:
                        stop = True
                elif mode == "min" and depth > 1:
                    aux_score = min(aux_score, minimax_alphabeta(aux_state, max_depth, depth - 1, "max", alpha, beta))
                    beta = min(beta, aux_score)
                    if alpha >= beta:
                        stop = True
                else:
                    aux_score = min(aux_score, get_state_score_naive(aux_state, state))
                    beta = min(beta, aux_score)
                    if alpha >= beta:
                        stop = True
                if aux_score is not None:
                    scores.append((aux_score, i, j))
            j += 1
        i += 1
    # print(mode, depth, scores)
    if mode == "max" and depth == max_depth:
        if len(scores) > 0:
            best_result = max(scores, key=lambda x: x[0])
            scores = list(filter(lambda x: x[0] == best_result[0], scores))
            best_result = random.choice(scores)
            if best_result[0] != -oo:
                best_state = make_transition(state, best_result[1], best_result[2])
            else:
                best_state = computer_moves_based_on_one_level_results(state)
            return best_state
        else:
            return computer_moves_based_on_one_level_results(state)
    elif mode == "max":
        if len(scores) > 0:
            best_result = max(scores, key=lambda x: x[0])
            return best_result[0]
        else:
            return -oo
    else:
        if len(scores) > 0:
            best_result = min(scores, key=lambda x: x[0])
            return best_result[0]
        else:
            return oo


if __name__ == '__main__':
    play(ProblemState())
