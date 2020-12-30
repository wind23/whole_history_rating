import math
from .player_day import PlayerDay
from .game import UnstableRatingException

class Player:
  
    def __init__(self, name, config):
        self.name = name
        self.debug = config.get('debug', False)
        self.w2 = (math.sqrt(config['w2']) * math.log(10.) / 400.) ** 2.  # Convert from elo^2 to r^2
        self.virtual_games = config['virtual_games']
        self.days = []
  
    def inspect(self):
        return "%s:(%s)" % (self, self.name)
  
    def log_likelihood(self):
        sum_ = 0.0
        sigma2 = self.compute_sigma2()
        n = len(self.days)
        for i in range(n):
            prior = 0
            if i < n - 1:
                rd = self.days[i].r - self.days[i + 1].r
                prior += (1. /(math.sqrt(2 * math.pi * sigma2[i]))) * math.exp(- (rd ** 2) / 2. / sigma2[i]) 
            if i > 0:
                rd = self.days[i].r - self.days[i - 1].r
                prior += (1. /(math.sqrt(2 * math.pi * sigma2[i - 1]))) * math.exp(- (rd ** 2) / 2. / sigma2[i - 1]) 
            if prior == 0:
                sum_ += self.days[i].log_likelihood()
            else:
                if math.isinf(self.days[i].log_likelihood()) or math.isinf(math.log(prior)):
                    print ("Infinity at %s: %f + %f: prior = %f, days = %s" % (self.inspect(), self.days[i].log_likelihood(), math.log(prior), prior, map(lambda d: d.inspect(), self.days)))
                    exit(0)
                sum_ += self.days[i].log_likelihood() + math.log(prior)
        return sum_

    def hessian(self, days, sigma2):
        n = len(days)
        mat = [[0.0 for i in range(n)] for j in range(n)]
        for row in range(n):
            for col in range(n):
                if row == col:
                    prior = 0.
                    if row < n - 1:
                        prior += - 1.0 / sigma2[row]
                    if row > 0:
                        prior += - 1.0 / sigma2[row - 1]
                    mat[row][col] = days[row].log_likelihood_second_derivative() + prior - 0.001
                elif row == col - 1:
                    mat[row][col] = 1.0 / sigma2[row]
                elif row == col + 1:
                    mat[row][col] = 1.0 / sigma2[col]
        return mat

    def gradient(self, r, days, sigma2):
        n = len(days)
        g = [0.0 for i in range(n)]
        for idx in range(n):
            day = days[idx]
            prior = 0
            if idx < n - 1:
                prior += - (r[idx] - r[idx + 1]) / sigma2[idx]
            if idx > 0:
                prior += - (r[idx] - r[idx - 1]) / sigma2[idx - 1]
            if self.debug:
                print ("g[%d] = %f + %f" % (idx, day.log_likelihood_derivative(), prior))
            g[idx] = day.log_likelihood_derivative() + prior
        return g
  
    def run_one_newton_iteration(self):
        for day in self.days:
            day.clear_game_terms_cache()
      
        if len(self.days) == 1:
            self.days[0].update_by_1d_newtons_method()
        elif len(self.days) > 1:
            self.update_by_ndim_newton()
  
    def compute_sigma2(self):
        sigma2 = [0.0 for i in range(len(self.days) - 1)]
        for i in range(len(self.days) - 1):
            d1 = self.days[i]
            d2 = self.days[i + 1]
            sigma2[i] = abs(d2.day - d1.day) * self.w2
        return sigma2
  
    def update_by_ndim_newton(self):
        r = list(map(lambda d: d.r, self.days))
      
        if self.debug:
            print ("Updating %s" % self.inspect())
            for day in self.days:
                print ("day[%d] r = %f" % (day.day, day.r))
                print ("day[%d] win terms = %s" % (day.day, day.won_game_terms()))
                print ("day[%d] win games = %s" % (day.day, day.won_games))
                print ("day[%d] draw terms = %s" % (day.day, day.draw_game_terms()))
                print ("day[%d] draw games = %s" % (day.day, day.draw_games))
                print ("day[%d] lost terms = %s" % (day.day, day.lost_game_terms()))
                print ("day[%d] lost games = %s" % (day.day, day.lost_games))
                print ("day[%d] log(p) = %f" % (day.day, day.log_likelihood()))
                print ("day[%d] dlp = %f" % (day.day, day.log_likelihood_derivative()))
                print ("day[%d] dlp2 = %f" % (day.day, day.log_likelihood_second_derivative()))
      
        # sigma squared (used in the prior)
        sigma2 = self.compute_sigma2()
      
        h = self.hessian(self.days, sigma2)
        g = self.gradient(r, self.days, sigma2)

        n = len(r)
      
        a = [0.0 for i in range(n)]
        d = [h[0][0]] + [0.0 for i in range(n - 1)]
        b = [h[0][1]] + [0.0 for i in range(n - 1)]

        for i in range(1, n):
            a[i] = h[i][i - 1] / d[i - 1]
            d[i] = h[i][i] - a[i] * b[i - 1]
            if i < n - 1:
                b[i] = h[i][i + 1]
      
        y = [g[0]] + [0.0 for i in range(n - 1)]
        for i in range(1, n):
            y[i] = g[i] - a[i] * y[i - 1]
      
        x = [0.0 for i in range(n)]
        x[n - 1] = y[n - 1] / d[n - 1]
        for i in range(n - 2, -1, -1):
            x[i] = (y[i] - b[i] * x[i + 1]) / d[i]

        new_r = [0.0 for i in range(n)]
        for i in range(n):
            new_r[i] = r[i] - x[i]
      
        for r_ in new_r:
          if r_ > 650:
            raise UnstableRatingException("Unstable r (%s) on player %s" % (new_r, self.inspect()))
      
        if self.debug:
            print ("Hessian = %s" % h)
            print ("gradient = %s" % g)
            print ("a = %s" % a)
            print ("d = %s" % d)
            print ("b = %s" % b)
            print ("y = %s" % y)
            print ("x = %s" % x)
            print ("%s (%s) => (%s)" % (self.inspect(), r, new_r))
      
        for idx in range(len(self.days)):
            day = self.days[idx]
            day.r = day.r - x[idx]

    def covariance(self):
        r = list(map(lambda d: d.r, self.days))
      
        sigma2 = self.compute_sigma2()
        h = self.hessian(self.days, sigma2)
      
        n = len(r)

        a = [0.0 for i in range(n)]
        d = [h[0][0]] + [0.0 for i in range(n - 1)]
        if n > 1:
            b = [h[0][1]] + [0.0 for i in range(n - 1)]
        else:
            b = [0.0]
       
        for i in range(1, n):
            a[i] = h[i][i - 1] / d[i - 1]
            d[i] = h[i][i] - a[i] * b[i - 1]
            if i < n - 1:
                b[i] = h[i][i + 1]
      
        dp = [0.0 for i in range(n)]
        dp[n - 1] = h[n - 1][n - 1]    
        bp = [0.0 for i in range(n)]
        bp[n - 1] = h[n - 1][n - 2]
        ap = [0.0 for i in range(n)]
        for i in range(n - 2, -1, -1):
          ap[i] = h[i][i + 1] / dp[i + 1]
          dp[i] = h[i][i] - ap[i] * bp[i + 1]
          bp[i] = h[i][i - 1]
      
        v = [0.0 for i in range(n)]
        for i in range(n - 1):
            v[i] = dp[i + 1] / (b[i] * bp[i + 1] - d[i] * dp[i + 1])
        v[n - 1] = -1. / d[n - 1]
      
        mat = [[0.0 for i in range(n)] for j in range(n)]
        for row in range(n):
            for col in range(n):
                if row == col:
                    mat[row][col] = v[row]
                elif row == col - 1:
                    mat[row][col] = - a[col] * v[col]
        return mat
    
    def update_uncertainty(self):
        if len(self.days) > 0:
            c = self.covariance()
            u = [c[i][i] for i in range(len(self.days))] # u = variance
            for i in range(len(self.days)):
                self.days[i].uncertainty = u[i]
  
    def add_game(self, game):
        if len(self.days) == 0 or self.days[-1].day != game.day:
            new_pday = PlayerDay(self, game.day)
            if len(self.days) == 0:
                new_pday.is_first_day = True
                new_pday.set_gamma(1.)
            else:
                new_pday.set_gamma(self.days[-1].gamma())
            self.days.append(new_pday)
        if game.white_player == self:
            game.wpd = self.days[-1]
        else:
            game.bpd = self.days[-1]
        self.days[-1].add_game(game)

