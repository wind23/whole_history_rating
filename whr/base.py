from .game import Game
from .player import Player
from .game import UnstableRatingException

class Base:
    
    def __init__(self, config = {}):
        self.config = config
        self.config.setdefault('w2', 300.0)  # elo^2
        self.games = []
        self.players = {}
  
    def print_ordered_ratings(self):
        players = list(filter(lambda p: len(p.days) > 0, self.players.values()))
        for p in sorted(players, key = lambda p: p.days[-1].gamma(), reverse = True):
            if len(p.days) > 0:
                print ("%s\t%s" % (p.name, ';'.join(map(lambda pd: '%d,%.2f' % (pd.day, pd.elo()), p.days))))
  
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
    
    def create_game(self, black, white, winner, time_step, handicap, extras = {}):
        game = self.setup_game(black, white, winner, time_step, handicap, extras)
        return self.add_game(game)
  
    def add_game(self, game):
        game.white_player.add_game(game)
        game.black_player.add_game(game)
        if game.bpd == None:
            print ("Bad game: %d" % game.inspect())
        self.games.append(game)
        return game
    
    def iterate(self, count):
        for _ in range(count):
            self.run_one_iteration()
        for player in self.players.values():
            player.update_uncertainty()
  
    def run_one_iteration(self):
        for player in self.players.values():
            player.run_one_newton_iteration()
