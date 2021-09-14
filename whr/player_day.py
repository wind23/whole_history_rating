import math

class PlayerDay:

    def __init__(self, player, day):
        self.day = day
        self.player = player
        self.is_first_day = False
        self.virtual_games = player.virtual_games
        self.won_games = []
        self.draw_games = []
        self.lost_games = []
        self.won_game_terms_cache = None
        self.draw_game_terms_cache = None
        self.lost_game_terms_cache = None
  
    def set_gamma(self, gamma):
        self.r = math.log(gamma)
  
    def gamma(self):
        return math.exp(self.r)
  
    def set_elo(self, elo):
        self.r = elo * (math.log(10.) / 400.0)
  
    def elo(self):
        return (self.r * 400.0)/(math.log(10.))
  
    def clear_game_terms_cache(self):
        self.won_game_terms_cache = None
        self.draw_game_terms_cache = None
        self.lost_game_terms_cache = None
  
    def won_game_terms(self):
        if self.won_game_terms_cache == None:
            self.won_game_terms_cache = []
            for g in self.won_games:
                other_gamma = g.opponents_adjusted_gamma(self.player)
                if other_gamma == 0. or math.isnan(other_gamma) or math.isinf(other_gamma):
                    print ("other_gamma (%s) = %s" % (g.opponent(self.player).inspect(), other_gamma))
                self.won_game_terms_cache.append([1.0, 0.0, 1.0, other_gamma])
        return self.won_game_terms_cache

    def draw_game_terms(self):
        if self.draw_game_terms_cache == None:
            self.draw_game_terms_cache = []
            for g in self.draw_games:
                other_gamma = g.opponents_adjusted_gamma(self.player)
                if other_gamma == 0. or math.isnan(other_gamma) or math.isinf(other_gamma):
                    print ("other_gamma (%s) = %s" % (g.opponent(self.player).inspect(), other_gamma))
                self.draw_game_terms_cache.append([0.5, 0.5 * other_gamma, 1.0, other_gamma])
            if self.is_first_day:
                for _ in range(self.virtual_games):
                    self.draw_game_terms_cache.append([0.5, 0.5, 1.0, 1.0])  # draw with virtual player ranked with gamma = 1.0
        return self.draw_game_terms_cache
    
    def lost_game_terms(self):
        if self.lost_game_terms_cache == None:
            self.lost_game_terms_cache = []
            for g in self.lost_games:
                other_gamma = g.opponents_adjusted_gamma(self.player)
                if other_gamma == 0. or math.isnan(other_gamma) or math.isinf(other_gamma):
                    print ("other_gamma (%s) = %s" % (g.opponent(self.player).inspect(), other_gamma))
                self.lost_game_terms_cache.append([0.0, other_gamma, 1.0, other_gamma])
        return self.lost_game_terms_cache
  
    def log_likelihood_second_derivative(self):
        sum_ = 0.0
        gamma = self.gamma()
        for _, _, c, d in (self.won_game_terms() + self.draw_game_terms() + self.lost_game_terms()):
            sum_ += (c * d) / ((c * gamma + d) ** 2.0)
        if math.isnan(gamma) or math.isnan(sum_):
            print ("won_game_terms = %s" % self.won_game_terms())
            print ("draw_game_terms = %s" % self.draw_game_terms())
            print ("lost_game_terms = %s" % self.lost_game_terms())
        return -1. * gamma * sum_

    def log_likelihood_derivative(self):   
        tally = 0.0
        gamma = self.gamma()
        for _, _, c, d in (self.won_game_terms() + self.draw_game_terms() + self.lost_game_terms()):
            tally += c / (c * gamma + d)
        return len(self.won_game_terms()) + 0.5 * len(self.draw_game_terms()) - gamma * tally

    def log_likelihood(self):
        tally = 0.0
        for a, b, c, d in self.won_game_terms():
            tally += math.log(a * self.gamma())
            tally -= math.log(c * self.gamma() + d)
        for a, b, c, d in self.draw_game_terms():
            tally += math.log(a * 2. * self.gamma()) * 0.5
            tally += math.log(b * 2.) * 0.5
            tally -= math.log(c * self.gamma() + d)
        for a, b, c, d in self.lost_game_terms():
            tally += math.log(b)
            tally -= math.log(c * self.gamma() + d)
        return tally
  
    def add_game(self, game):
        if(game.winner == "D"):
            self.draw_games.append(game)
        elif (game.winner == "W" and game.white_player == self.player) or (game.winner == "B" and game.black_player == self.player):
            self.won_games.append(game)
        else:
            self.lost_games.append(game)

    def update_by_1d_newtons_method(self):
        dlogp = self.log_likelihood_derivative()
        d2logp = self.log_likelihood_second_derivative()
        dr = dlogp / d2logp
        new_r = self.r - dr
        self.r = new_r
