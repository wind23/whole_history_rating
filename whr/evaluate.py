import math
from .game import Game

class Evaluate:

    def __init__(self, base):
        self.ratings_by_players = {}
        for name, player in base.players.items():
            ratings = list(map(lambda d: [d.day, d.elo()], player.days))
            self.ratings_by_players[name] = sorted(ratings)

    def get_rating(self, name, day, ignore_null_players=True):
        min_day, min_rating = None, None
        max_day, max_rating = None, None
        if not name in self.ratings_by_players.keys():
            if ignore_null_players:
                return None
            else:
                return 0.
        ratings = self.ratings_by_players[name]
        for i in range(len(ratings)):
            if ratings[i][0] <= day:
                if (not min_day) or (ratings[i][0] >= min_day):
                    min_day = ratings[i][0]
                    min_rating = ratings[i][1]
            if ratings[i][0] >= day:
                if (not max_day) or (ratings[i][0] <= max_day):
                    max_day = ratings[i][0]
                    max_rating = ratings[i][1]
        if not min_day:
            ret = max_rating
        elif not max_day:
            ret = min_rating
        elif max_day <= min_day:
            ret = max_rating
        else:
            ret = ((max_day - day) * min_rating + (day - min_day) * max_rating) * 1.0 / (max_day - min_day)
        return ret

    def evaluate_single_game(self, game, ignore_null_players=True):
        black_rating = self.get_rating(game.black_player, game.day, ignore_null_players=ignore_null_players)
        white_rating = self.get_rating(game.white_player, game.day, ignore_null_players=ignore_null_players)
        if black_rating == None or white_rating == None:
            return None
        if game.handicap_proc:
            black_advantage = game.handicap_proc(game)
        else:
            black_advantage = game.handicap
        white_gamma = 10. ** (white_rating / 400.)
        black_adjusted_gamma = 10. ** ((black_rating + black_advantage) / 400.)

        if game.winner == 'W':
            return white_gamma/(white_gamma + black_adjusted_gamma)
        elif game.winner == 'B':
            return black_adjusted_gamma/(white_gamma + black_adjusted_gamma)
        else:
            return (white_gamma * black_adjusted_gamma) ** 0.5 / (white_gamma + black_adjusted_gamma)

    def evaluate_ave_log_likelihood_games(self, games, ignore_null_players=True):
        sum_ = 0.
        games = self.list_to_games(games)
        game_count = 0
        for game in games:
            game_likelihood = self.evaluate_single_game(game, ignore_null_players=ignore_null_players)
            if game_likelihood != None:
                sum_ += math.log(game_likelihood)
                game_count += 1
        return sum_ / game_count
        
    def list_to_games(self, game_list):
        games = []
        for game in game_list:
            black, white, winner, time_step = game[:4]
            handicap = 0
            if len(game) >= 5:
                handicap = game[4]
            extras = {}
            if len(game) >= 5:
                extras = game[5]
            games.append(Game(black, white, winner, time_step, handicap, extras))
        return games
