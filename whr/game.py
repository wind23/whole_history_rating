import math

class UnstableRatingException(RuntimeError):
    pass

class Game:

    def __init__(self, black, white, winner, time_step, handicap = 0, extras = {}):
        self.day = time_step
        self.white_player = white
        self.black_player = black
        self.winner = winner
        self.extras = extras
        self.handicap = handicap if handicap else 0
        self.wpd = None
        self.bpd = None
        if callable(handicap):
            self.handicap_proc = handicap
        else:
            self.handicap_proc = None
  
    def opponents_adjusted_gamma(self, player):
        if self.handicap_proc:
            black_advantage = self.handicap_proc(self)
        else:
            black_advantage = self.handicap

        if player == self.white_player:
            opponent_elo = self.bpd.elo() + black_advantage
        elif player == self.black_player:
            opponent_elo = self.wpd.elo() - black_advantage
        else:
            raise ValueError("No opponent for %s, since they're not in this game: %s." % (player.inspect(), self.inspect()))

        try:
            rval = 10. ** (opponent_elo / 400.0)
        except OverflowError:
            rval = float('inf')
        if rval == 0. or math.isinf(rval) or math.isnan(rval):
            raise UnstableRatingException("bad adjusted gamma: %s" % self.inspect())

        return rval
    
    def opponent(self, player):
        if player == self.white_player:
            return self.black_player
        elif player == self.black_player:
            return self.white_player
  
    def inspect(self):
        return "%s: W:%s(%.2f) B:%s(%.2f) winner = %s, handicap = %s" % (self, self.white_player.name, self.wpd.r if self.wpd else '?', self.black_player.name, self.bpd.r if self.bpd else '?', self.winner, self.handicap)
  
    def likelihood(self):
        if self.winner == 'W':
            return self.white_win_probability()
        elif self.winner == 'B':
            return self.black_win_probability()
        else:
            return (self.white_win_probability() * self.black_win_probability()) ** 0.5
  
    # This is the Bradley-Terry Model
    def white_win_probability(self):
        return self.wpd.gamma()/(self.wpd.gamma() + self.opponents_adjusted_gamma(self.white_player))
  
    def black_win_probability(self):
        return self.bpd.gamma()/(self.bpd.gamma() + self.opponents_adjusted_gamma(self.black_player))
