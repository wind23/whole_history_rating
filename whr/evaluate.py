import math

class Evaluate:

    def __init__(self, base):
        self.ratings_by_players = {}
        for name, player in base.players.items():
            ratings = list(map(lambda d: [d.day, d.elo()], player.days))
            self.ratings_by_players[name] = sorted(ratings)

    def get_rating(self, name, day):
        min_day, min_rating = None, None
        max_day, max_rating = None, None
        if not name in self.ratings_by_players.keys():
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

    def evaluate_single_game(self, game):
        black_rating = self.get_rating(game.black_player, game.day)
        white_rating = self.get_rating(game.white_player, game.day)
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

    def evaluate_ave_log_likelihood_games(self, games):
        sum_ = 0.
        for game in games:
            sum_ += math.log(self.evaluate_single_game(game))
        return sum_ / len(games)
        

