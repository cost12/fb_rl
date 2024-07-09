import random
import math

class Position:
    """
    Describes the location of an object on a 10 by 3 field with top left being (0,0)
    """
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

class Body:
    """
    Represents the body of a player
    """
    def __init__(self, x, y):
        self.position = Position(x,y)

    def x(self):
        return self.position.x
    
    def y(self):
        return self.position.y

class Player:
    """
    Represents a player
    """
    OFFENSE = 0
    DEFENSE = 1
    SPECIAL = 2
    def __init__(self, body:Body, team:int):
        self.body = body
        self.team = team
        self.has_ball = False

    def x(self):
        return self.body.x()
    
    def y(self):
        return self.body.y()

class Ball:

    def __init__(self):
        self.position = None

class Timing:
    """
    Represents how much time is left in the game
    """
    def __init__(self):
        self.quarter = 0
        self.quarter_len = 60
        self.time_left = 60
        self.over = False
        self.is_halftime = False

    def run_clock(self):
        if not self.is_over() and self.time_left > 0:
            self.time_left -= 1

    def end_play(self):
        if not self.is_over() and self.time_left <= 0:
            if self.quarter == 1:
                self.is_halftime = True
            if self.quarter == 3:
                self.over = True
                return
            self.time_left = self.quarter_len
            self.quarter += 1

    def halftime(self):
        self.is_halftime = False

    def is_over(self):
        return self.over

class FieldPos:

    def __init__(self):
        self.down = 0
        self.yd_line = 25
        self.to_first = 10
        self.possession = 0 # 0 or 1
        self.direction = 1  # 1 or -1

    def fg_dist(self) -> int:
        if self.direction == -1:
            return self.yd_line + 17
        else:
            return 100 - self.yd_line + 17
        
    def halftime(self):
        self.down = 0
        self.to_first = 10
        self.possession = 1
        self.direction = -1
        self.yd_line = 75

    def kickoff(self):
        self.change_possesion()
        self.yd_line = 50 - 25*self.direction

    def change_possesion(self):
        self.down = 0
        self.to_first = 10
        if self.possession == 1:
            self.possession = 0
        else:
            self.possession = 1
        self.direction *= -1

    def is_touchdown(self, gain):
        check = self.yd_line + gain*self.direction
        if check >= 100 and self.direction > 0:
            return True
        elif check <= 0 and self.direction < 0:
            return True
        return False
    
    def move(self, dist):
        self.yd_line += dist*self.direction
        if self.yd_line >= 100:
            self.yd_line = 80
        elif self.yd_line <= 0:
            self.yd_line = 20

    def gain(self, dist, is_score) -> bool:
        self.yd_line += dist*self.direction
        if dist >= self.to_first:
            self.down = 0
            self.to_first = 10
        else:
            self.down += 1
            self.to_first -= dist
            if self.down >= 4 and not is_score:
                self.change_possesion()
                return False
        return True

class FootballState:

    def __init__(self):
        self.time = Timing()
        self.pos = FieldPos()
        self.t1_score = 0
        self.t2_score = 0

    def halftime(self):
        self.time.halftime()
        self.pos.halftime()

    def fg_dist(self) -> int:
        return self.pos.fg_dist()
    
    def fg_miss(self):
        self.time.run_clock()
        self.time.end_play()
        self.pos.move(-7)
        self.pos.down = 4

    def punt(self, dist):
        self.time.run_clock()
        self.time.end_play()
        self.pos.move(dist)
        self.pos.down = 4

    def fg(self):
        self.time.run_clock()
        self.time.end_play()
        if self.pos.possession == 0:
            self.t1_score += 3
        else:
            self.t2_score += 3

    def touchdown(self):
        if self.pos.possession == 0:
            self.t1_score += 7
        else:
            self.t2_score += 7

    def kickoff(self):
        self.pos.kickoff()

class FootballEnv:
    NO_MOVE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4
    #RESET = 5
    KICK = 5
    PUNT = 6

    EMPTY=0
    OFFENSE=1
    DEFENSE=2

    def __init__(self, *, width=3,length=10,off_speed=2):
        self.width=width
        self.length=length
        self.off_speed = off_speed
        self.viewers = []
        self.state = FootballState()
        self.points_scored = 0

        self.reset()

    def get_state(self):
        board = [self.field_rep]
        state = [self.wraps, self.wait, self.state.t1_score,self.state.t2_score, \
                 self.state.pos.down, self.yd_line(), self.state.pos.to_first, self.possession(), \
                 self.state.pos.direction, self.state.time.quarter, self.state.time.time_left]
        return board, state 

    def reset(self, total_reset=False):
        if total_reset:
            self.state = FootballState()
        if self.points_scored > 0:
            self.state.kickoff()
        self.wraps = 0
        self.yards_gained = 0
        self.is_turnover = False
        self.in_play = False
        self.is_down = False
        self.points_scored = 0
        self.wait = 0
        if self.state.pos.direction > 0:
            self.offense = Player(Body(0,1),Player.OFFENSE)
            self.defense = list[Player]()
            #self.defense.append(Player(Body(3,0),Player.DEFENSE))
            self.defense.append(Player(Body(3,1),Player.DEFENSE))
            #self.defense.append(Player(Body(3,2),Player.DEFENSE))
            self.defense.append(Player(Body(5,1),Player.DEFENSE))
            self.defense.append(Player(Body(8,1),Player.DEFENSE))
        else:
            self.offense = Player(Body(self.length-1,1),Player.OFFENSE)
            self.defense = list[Player]()
            #self.defense.append(Player(Body(self.length-4,0),Player.DEFENSE))
            self.defense.append(Player(Body(self.length-4,1),Player.DEFENSE))
            #self.defense.append(Player(Body(self.length-4,2),Player.DEFENSE))
            self.defense.append(Player(Body(self.length-6,1),Player.DEFENSE))
            self.defense.append(Player(Body(self.length-9,1),Player.DEFENSE))

        self.field_rep = [[] for _ in range(self.width)]
        for r in range(self.width):
            for c in range(self.length):
                self.field_rep[r].append(FootballEnv.EMPTY)
        self.field_rep[self.offense.y()][self.offense.x()] = FootballEnv.OFFENSE
        for defender in self.defense:
            self.field_rep[defender.y()][defender.x()] = FootballEnv.DEFENSE

    def kick(self):
        if self.can_kick():
            rand = random.random()
            prob = -math.tanh(0.1*self.state.fg_dist()-0.1*55)/2 + 0.5
            if rand < prob:
                self.state.fg()
                self.points_scored = 3
            else:
                self.state.fg_miss()
            self.is_down = True

    def punt(self):
        if self.can_punt():
            dist = int(random.gauss(45,5))
            self.state.punt(dist)
            self.is_down = True

    def gain(self):
        if self.dir() == 1:
            return self.length*self.wraps + self.offense.x()
        else:
            return self.length*self.wraps + self.length - 1 - self.offense.x()

    def reset_play(self):
        if self.is_down and not self.is_over():
            self.is_turnover = not self.state.pos.gain(self.gain(),self.points_scored>0)
            self.state.time.end_play()
            if self.state.time.is_halftime:
                self.state.halftime()
            if not self.is_over():
                self.reset()
            for viewer in self.viewers:
                viewer.update_env(self)
        
    def move_player(self, player:Player, move:int) -> None:
        if player == self.offense:
            self.yards_gained = 0
        if move == FootballEnv.LEFT:
            if player.x() - 1 >= 0:
                if self.field_rep[player.y()][player.x()-1] == FootballEnv.DEFENSE and player.team == Player.OFFENSE or \
                   self.field_rep[player.y()][player.x()-1] == FootballEnv.OFFENSE and player.team == Player.DEFENSE:
                    self.is_down = True
                    return
                self.field_rep[player.y()][player.x()] = FootballEnv.EMPTY
                player.body.position.x -= 1
                if player.team == Player.DEFENSE:
                    self.field_rep[player.y()][player.x()] = FootballEnv.DEFENSE
                else:
                    self.field_rep[player.y()][player.x()] = FootballEnv.OFFENSE
                    self.yards_gained = self.state.pos.direction*-1
            elif self.dir() == 1:
                if player.team == Player.OFFENSE and player.x() == 0 and self.wraps > 0: # and self.field_rep[player.y()][self.length-1] == FootballEnv.EMPTY:
                    if self.field_rep[player.y()][self.length-1] == FootballEnv.DEFENSE and player.team == Player.OFFENSE or \
                       self.field_rep[player.y()][self.length-1] == FootballEnv.OFFENSE and player.team == Player.DEFENSE:
                        self.is_down = True
                        return
                    self.field_rep[player.y()][player.x()] = FootballEnv.EMPTY
                    player.body.position.x = self.length-1
                    self.field_rep[player.y()][player.x()] = FootballEnv.OFFENSE
                    self.wraps -= 1
                    self.yards_gained = -1
            elif self.dir() == -1:
                if player.team == Player.OFFENSE and player.x() == 0: # and self.field_rep[player.y()][self.length-1] == FootballEnv.EMPTY:
                    if self.field_rep[player.y()][self.length-1] == FootballEnv.DEFENSE and player.team == Player.OFFENSE or \
                       self.field_rep[player.y()][self.length-1] == FootballEnv.OFFENSE and player.team == Player.DEFENSE:
                        self.is_down = True
                        return
                    self.field_rep[player.y()][player.x()] = FootballEnv.EMPTY
                    player.body.position.x = self.length-1
                    self.field_rep[player.y()][player.x()] = FootballEnv.OFFENSE
                    self.wraps += 1
                    self.yards_gained = 1
        elif move == FootballEnv.RIGHT:
            if player.x() + 1 < self.length:
                if self.field_rep[player.y()][player.x()+1] == FootballEnv.DEFENSE and player.team == Player.OFFENSE or \
                   self.field_rep[player.y()][player.x()+1] == FootballEnv.OFFENSE and player.team == Player.DEFENSE:
                    self.is_down = True
                    return
                self.field_rep[player.y()][player.x()] = FootballEnv.EMPTY
                player.body.position.x += 1
                if player.team == Player.DEFENSE:
                    self.field_rep[player.y()][player.x()] = FootballEnv.DEFENSE
                else:
                    self.field_rep[player.y()][player.x()] = FootballEnv.OFFENSE
                    self.yards_gained = self.state.pos.direction
            elif self.dir() == 1:
                if player.team == Player.OFFENSE and player.x() + 1 == self.length: # and self.field_rep[player.y()][0] == FootballEnv.EMPTY:
                    if self.field_rep[player.y()][0] == FootballEnv.DEFENSE and player.team == Player.OFFENSE or \
                       self.field_rep[player.y()][0] == FootballEnv.OFFENSE and player.team == Player.DEFENSE:
                        self.is_down = True
                        return
                    self.field_rep[player.y()][player.x()] = FootballEnv.EMPTY
                    player.body.position.x = 0
                    self.field_rep[player.y()][player.x()] = FootballEnv.OFFENSE
                    self.wraps += 1
                    self.yards_gained = 1
            elif self.dir() == -1:
                if player.team == Player.OFFENSE and self.wraps > 0 and player.x() + 1 == self.length: # and self.field_rep[player.y()][0] == FootballEnv.EMPTY:
                    if self.field_rep[player.y()][0] == FootballEnv.DEFENSE and player.team == Player.OFFENSE or \
                       self.field_rep[player.y()][0] == FootballEnv.OFFENSE and player.team == Player.DEFENSE:
                        self.is_down = True
                        return
                    self.field_rep[player.y()][player.x()] = FootballEnv.EMPTY
                    player.body.position.x = 0
                    self.field_rep[player.y()][player.x()] = FootballEnv.OFFENSE
                    self.wraps -= 1
                    self.yards_gained = -1
        elif move == FootballEnv.UP:
            if player.y() - 1 >= 0:
                if self.field_rep[player.y()-1][player.x()] == FootballEnv.DEFENSE and player.team == Player.OFFENSE or \
                   self.field_rep[player.y()-1][player.x()] == FootballEnv.OFFENSE and player.team == Player.DEFENSE:
                    self.is_down = True
                    return
                self.field_rep[player.y()][player.x()] = FootballEnv.EMPTY
                player.body.position.y -= 1
                if player.team == Player.DEFENSE:
                    self.field_rep[player.y()][player.x()] = FootballEnv.DEFENSE
                else:
                    self.field_rep[player.y()][player.x()] = FootballEnv.OFFENSE
        elif move == FootballEnv.DOWN:
            if player.y() + 1 < self.width:
                if self.field_rep[player.y()+1][player.x()] == FootballEnv.DEFENSE and player.team == Player.OFFENSE or \
                   self.field_rep[player.y()+1][player.x()] == FootballEnv.OFFENSE and player.team == Player.DEFENSE:
                    self.is_down = True
                    return
                self.field_rep[player.y()][player.x()] = FootballEnv.EMPTY
                player.body.position.y += 1
                if player.team == Player.DEFENSE:
                    self.field_rep[player.y()][player.x()] = FootballEnv.DEFENSE
                else:
                    self.field_rep[player.y()][player.x()] = FootballEnv.OFFENSE
        elif move == FootballEnv.NO_MOVE:
            pass

    def get_legal_moves(self, player:Player) -> set[int]:
        moves = set[int]()
        if player.x() - 1 >= 0 and not (self.field_rep[player.y()][player.x()-1] == FootballEnv.DEFENSE):
            moves.add(FootballEnv.LEFT)
        if player.x() + 1 < self.length and not (self.field_rep[player.y()][player.x()+1] == FootballEnv.DEFENSE):
            moves.add(FootballEnv.RIGHT)
        if player.y() - 1 >= 0 and not (self.field_rep[player.y()-1][player.x()] == FootballEnv.DEFENSE):
            moves.add(FootballEnv.UP)
        if player.y() + 1 < self.width and not (self.field_rep[player.y()+1][player.x()] == FootballEnv.DEFENSE):
            moves.add(FootballEnv.DOWN)
        return moves
        
    def move_offense(self, move:int) -> None:
        self.move_player(self.offense, move)

    def move_defense(self) -> None:
        if len(self.defense) == 0:
            return
        all_moves = dict[Player,set[int]]()
        total_moves = 0
        # loop and find all legal moves that move towards the offense
        for defender in self.defense:
            legal = self.get_legal_moves(defender)
            good = set[int]()
            if defender.x() > self.offense.x():
                good.add(FootballEnv.LEFT)
            elif defender.x() < self.offense.x():
                good.add(FootballEnv.RIGHT)
            if defender.y() > self.offense.y():
                good.add(FootballEnv.UP)
            elif defender.y() < self.offense.y():
                good.add(FootballEnv.DOWN)
            moves = legal.intersection(good)
            total_moves += len(moves)
            all_moves[defender] = moves
        rand = random.randint(0,total_moves-1)
        # loop and find which move has been randomly selected
        for defender in self.defense:
            if rand < len(all_moves[defender]):
                move = list(all_moves[defender])[rand]
                self.move_player(defender,move)
                return
            else:
                rand -= len(all_moves[defender])

    def step(self, move:int) -> tuple: # state, reward, done #, change of possession, drive reward
        if 0:
            if self.is_down:
                if move == FootballEnv.RESET:
                    self.reset_play()
                return
        if self.can_kick() and move == FootballEnv.KICK:
            self.kick()
            points = self.points_scored
            self.reset_play()
            return self.get_state(), points, self.is_over()
        elif self.can_punt() and move == FootballEnv.PUNT:
            self.punt()
            self.reset_play()
            return self.get_state(), 0, self.is_over()
        self.in_play = True
        self.move_offense(move)
        points = 0
        if self.state.pos.is_touchdown(self.gain()):
            self.is_down = True
            self.points_scored = 7
            points = 7
            self.state.touchdown()
        self.wait += 1
        if self.wait >= self.off_speed and not self.is_down:
            self.wait = 0
            self.move_defense()
            self.state.time.run_clock()
        down = False
        if self.is_down:
            down = True
        if self.is_down: # don't want to waste rl steps learning to reset
            self.reset_play()
        for viewer in self.viewers:
            viewer.update_env(self)
        #rew = 0
        #if self.gain() >= self.dist():
        #    rew = 10000
        return self.get_state(), self.reward(points, self.yards_gained, down), down # self.is_over()
    
    def reward(self, points, yards_gained, down):
        if down and points == 0:
            return yards_gained-0.2 + 0.01
        elif down and points > 0:
            return points + yards_gained + 0.01
        else:
            return points + yards_gained + 0.01

    
    def t1(self):
        return "Home"
    
    def t2(self):
        return "Away"
    
    def s1(self):
        return self.state.t1_score
    
    def s2(self):
        return self.state.t2_score
    
    def to1(self):
        return 0
    
    def to2(self):
        return 0
    
    def q(self):
        return self.state.time.quarter
    
    def time_str(self):
        time = int(self.state.time.time_left/self.state.time.quarter_len *15*60)
        min = time//60
        sec = time%60
        return f"{min}:{sec:02d}"
    
    def down(self):
        return self.state.pos.down
    
    def dist(self):
        return self.state.pos.to_first
    
    def yd_line(self):
        return self.state.pos.yd_line
    
    def dir(self):
        return self.state.pos.direction
    
    def possession(self):
        return self.state.pos.possession  

    def is_over(self):
        return self.state.time.is_over()

    def can_kick(self):
        return self.state.fg_dist() <= 66 and not self.in_play and not self.is_down
    
    def can_punt(self):
        return not self.in_play and not self.is_down

    def get_actions(self):
        actions = []
        if not self.is_down:
            actions.append(FootballEnv.NO_MOVE)
            actions.append(FootballEnv.LEFT)
            actions.append(FootballEnv.RIGHT)
            actions.append(FootballEnv.UP)
            actions.append(FootballEnv.DOWN)
        if 0:
            if self.is_down:
                actions.append(FootballEnv.RESET)
        if self.can_kick():
            actions.append(FootballEnv.KICK)
        if self.can_punt():
            actions.append(FootballEnv.PUNT)
        return actions