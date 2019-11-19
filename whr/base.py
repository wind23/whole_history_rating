from .game import Game
from .player import Player
from .game import UnstableRatingException

class Base:
    
    def __init__(self, config = {}):
        self.config = config
        self.config.setdefault('w2', 300.0)  # elo^2
        self.config.setdefault('virtual_games', 2)  # elo^2
        self.games = []
        self.players = {}
  
    def print_ordered_ratings(self):
        players = list(filter(lambda p: len(p.days) > 0, self.players.values()))
        for p in sorted(players, key = lambda p: p.days[-1].gamma(), reverse = True):
            if len(p.days) > 0:
                print ("%s\t%s" % (p.name, ';'.join(map(lambda pd: '%d,%.2f' % (pd.day, pd.elo()), p.days))))

    def get_ordered_ratings(self):
        players = list(filter(lambda p: len(p.days) > 0, self.players.values()))
        ratings = []
        for p in sorted(players, key = lambda p: p.days[-1].gamma(), reverse = True):
            if len(p.days) > 0:
                ratings.append((p.name, self.ratings_for_player(p.name)))
        return ratings
  
    def log_likelihood(self):
        score = 0.0
        for p in self.players.values():
            if len(p.days) > 0:
                score += p.log_likelihood()
        return score
  
    def player_by_name(self, name):
        if not name in self.players.keys():
            self.players[name] = Player(name, self.config)
        return self.players[name]
    
    def ratings_for_player(self, name):
        player = self.player_by_name(name)
        return list(map(lambda d: [d.day, d.elo(), d.uncertainty * 100.], player.days))
    
    def setup_game(self, black, white, winner, time_step, handicap, extras = {}):
        # Avoid self-played games (no info)
        if black == white:
            raise ValueError("Invalid game (black player == white player)")
    
        white_player = self.player_by_name(white)
        black_player = self.player_by_name(black)
        game = Game(black_player, white_player, winner, time_step, handicap, extras)
        return game

    def create_games(self, games):
        games.sort(key=lambda g:g[3])
        for game in games:
            black, white, winner, time_step = game[:4]
            handicap = 0
            if len(game) >= 5:
                handicap = game[4]
            extras = {}
            if len(game) >= 5:
                extras = game[5]
            self.create_game(black, white, winner, time_step, handicap, extras)
    
    def create_game(self, black, white, winner, time_step, handicap = 0, extras = {}):
        game = self.setup_game(black, white, winner, time_step, handicap, extras)
        return self.add_game(game)
  
    def add_game(self, game):
        game.white_player.add_game(game)
        game.black_player.add_game(game)
        if game.bpd == None:
            print ("Bad game: %d" % game.inspect())
        self.games.append(game)
        return game

    def iterate_until_converge(self, verbose=True):
        count = 0
        last_ratings = None
        best_iteration = None
        while True:
            sorted_players = sorted(self.players.items(), key = lambda x: x[0])
            ratings = []
            for player in sorted_players:
                for day in player[1].days:
                    ratings.append(round(day.elo() * 100))
            delta = 0
            if count > 0:
                for i in range(len(ratings)):
                    delta += abs(ratings[i] - last_ratings[i])
                if verbose:
                    print ('Iteration: %d, delta: %d' % (count, delta))
                if delta > 0:
                    best_iteration = count
                if count - best_iteration >= 10:
                    break
                last_ratings = ratings
            else:
                best_iteration = count
                last_ratings = ratings
            self.run_one_iteration()
            count += 1
        for player in self.players.values():
            player.update_uncertainty()
        return count

    def iterate(self, count):
        for _ in range(count):
            self.run_one_iteration()
        for player in self.players.values():
            player.update_uncertainty()
  
    def run_one_iteration(self):
        for player in self.players.values():
            player.run_one_newton_iteration()
