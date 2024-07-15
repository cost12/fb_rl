class Position:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.x_s = 0
        self.y_s = 0
        self.z_s = 0

class Limitations:

    def __init__(self):
        self.speed = 0
        self.strength = 0
        self.stamina = 0
        self.balance = 0
        self.catch = 0
        self.throw = 0
        self.kick = 0
        self.punt = 0
        self.block = 0
        self.footwork = 0

class Body:

    def __init__(self):
        self.limits = None
        self.position = None
        self.direction = 0
        self.height = 0
        self.weight = 0
        self.reach = 0
        self.field = None
        self.team = None

        self.balance = 0
        self.ball_security = 0

class Ball:

    def __init__(self):
        self.position = None

class Weather:
    RAIN = 0
    SNOW = 1

    def __init__(self):
        self.wind_x = 0
        self.wind_y = 0
        self.precip_level = 0
        self.precip_type = None
        self.field = None

class Stadium:
    OPEN = 0
    CLOSED = 1

    def __init__(self):
        self.type = 0
        self.location = None
        self.field = None

class Field:
    GRASS = 0
    TURF = 1

    def __init__(self):
        self.surface = 0
        self.width = 160/3 *3*12
        self.length = 120 *3*12

class Timing:

    def __init__(self):
        self.quarter = 0
        self.quarter_len = 0
        self.time_left = 0
        self.play_clock = 0
        self.t1_timeouts = 0
        self.t2_timeouts = 0

class FieldPos:

    def __init__(self):
        self.down = 0
        self.down_loc_x = 0
        self.down_loc_y = 0
        self.to_first = 0
        self.possession = 0
        self.direction = 0

class FootballState:

    def __init__(self):
        time = None
        pos = None
        self.t1_score = 0
        self.t2_score = 0


class FootballEnv:

    def __init__(self):
        self.stadium = None
        self.state = None
        self.players = []


    def advance(self):
        pass

