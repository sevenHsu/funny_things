import os
import sys
import time
import random
import numpy as np
from pynput.keyboard import KeyCode, Listener
from threading import Thread

WALL = "■"
SNAKE_HEAD = '●'
SNAKE_TAIL = '○'
INIT_SNAKE_LENGTH = 3
MAP_SIZE = 30
CAKE_SIZE = 2
SCORES = [1, 3, 5]  # three different score points with different area
SCORES_LEVEL = [30, 50, 100, 200]
# TODO: add stumbling block for snake
BLOCK = True
SPEED = 3  # init snake move speed,1,2,5,...,100
OVER_MSG1 = "Game over!!! Score: {0}"
OVER_MSG2 = "Press [y] for play again, [n] for exit!!!"


class SnakeGame:
    def __init__(self):
        # score
        self.total_score = 0

        # snake move speed
        self.speed = SPEED

        # game over
        self.game_over = False

        self.direct_dict = {'w': (-1, 0), 'd': (0, 1), 's': (1, 0), 'a': (0, -1)}  # y,x
        self.direct_list = ['w', 'd', 's', 'a']

        # random direct first
        self.direct = random.choice(list(self.direct_dict.keys()))

        # initialize snake
        self.snake = self._init_snake()

        # initialize matrix
        self._update_matrix(True)

        # first random cake
        self.cake_points = list()
        self._generate_cake()

        # update matrix again after generate cake
        self._update_matrix()

        # initialize pic
        self._update_pic()

    def _init_snake(self):
        snake = list()
        c = MAP_SIZE // 2
        dy, dx = self.direct_dict[self.direct]  # delta y,x
        for i in range(INIT_SNAKE_LENGTH):
            p = (c + i * dy, c + i * dx)
            snake.append(p)
        return snake

    def _init_matrix(self):
        matrix = np.asarray([[' '] * MAP_SIZE] * MAP_SIZE)
        matrix[0] = WALL
        matrix[-1] = WALL
        matrix[:, 0] = WALL
        matrix[:, -1] = WALL
        return matrix

    def _update_pic(self):
        self.pic = "\n".join(["".join(vector) for vector in self.matrix])

    def _update_snake(self, point):
        self._is_game_over(point)
        if not self.game_over:
            self.snake.append(point)
            if point in self.cake_points:
                self._add_score(point)
                self._generate_cake()
            else:
                self.snake.pop(0)

    def _update_matrix(self, first=False):
        if not self.game_over:
            self.matrix = self._init_matrix()
            for i, (y, x) in enumerate(self.snake):
                symbol = SNAKE_TAIL
                if i == self.snake.__len__() - 1:
                    symbol = SNAKE_HEAD
                self.matrix[y, x] = symbol
            if not first:
                for cake_y, cake_x in self.cake_points:
                    self.matrix[cake_y, cake_x] = SNAKE_HEAD

    def _update(self):
        snake_head = self.snake[-1]
        dy, dx = self.direct_dict[self.direct]
        point = (snake_head[0] + dy, snake_head[1] + dx)
        self._update_snake(point)
        self._update_matrix()
        self._update_pic()

    def _generate_cake(self):
        empty_y, empty_x = np.where(self.matrix == ' ')
        empty_points = list(zip(empty_y, empty_x))
        gen_cake_size = CAKE_SIZE - len(self.cake_points)
        for _ in range(gen_cake_size):
            idx = random.randint(0, len(empty_points))
            self.cake_points.append(empty_points[idx])
            empty_points.pop(idx)

    def _add_score(self, point):
        cake_y, cake_x = point
        if cake_y in [1, MAP_SIZE - 1] and cake_x in [1, MAP_SIZE - 1]:
            score = SCORES[2]
        elif cake_y in [1, MAP_SIZE - 1] or cake_x in [1, MAP_SIZE - 1]:
            score = SCORES[1]
        else:
            score = SCORES[0]
        self.cake_points.remove(point)
        self.total_score += score

    def _is_game_over(self, point):
        y, x = point
        self.game_over = self.matrix[y, x] != ' ' and (y, x) not in self.cake_points

    def _game_over(self):
        def print_over_msg():
            os.system('clear')
            print('\n' + OVER_MSG1.format(self.total_score).center(len(OVER_MSG2), ' '))
            print('\n' + OVER_MSG2)
            msg = input()
            return msg

        msg = print_over_msg().lower()
        while 'y' not in msg and 'n' not in msg:
            msg = print_over_msg().lower()
        if 'y' in msg:
            self.game_over = False
            self.__init__()
            self._disply()
        elif 'n' in msg:
            sys.exit()

    def _snake_move(self):
        while True:
            key = KeyCode().from_char(self.direct)
            self._on_press(key)
            del key
            speed = self.speed + np.digitize(self.total_score, SCORES_LEVEL)
            time.sleep(1 / speed)

    def _disply(self):
        """主进程循环"""
        while True and not self.game_over:
            os.system('clear')
            sys.stdout.write("\r\n{0}\n{1}".format(("Score:" + str(self.total_score)).center(MAP_SIZE, ' '), self.pic))
            sys.stdout.flush()
            time.sleep(0.05)
        self._game_over()

    def _on_press(self, key):
        try:
            if key.char in self.direct_dict:
                opp_direct = self.direct_list[(self.direct_list.index(self.direct) + 2) % 4]
                if key.char != opp_direct:
                    self.direct = key.char
                    self._update()
        except:
            pass

    def __call__(self, ):
        self.listener_thread = Listener(on_press=self._on_press)
        self.move_thread = Thread(target=self._snake_move, daemon=True)
        self.listener_thread.start()
        self.move_thread.start()

        self._disply()


if __name__ == '__main__':
    game = SnakeGame()
    game()
