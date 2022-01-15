import whr


class WholeHistoryRatingTest:

    def __init__(self):
        self.whr = whr.Base()

    def setup_game_with_elo(self, white_elo, black_elo, handicap):
        game = self.whr.create_game("black", "white", "W", 1, handicap)
        game.black_player.days[0].set_elo(black_elo)
        game.white_player.days[0].set_elo(white_elo)
        return game

    def test_even_game_between_equal_strength_players_should_have_white_winrate_of_50_percent(
            self):
        game = self.setup_game_with_elo(500, 500, 0)
        assert (abs(0.5 - game.white_win_probability()) < 0.0001)

    def test_handicap_should_confer_advantage(self):
        game = self.setup_game_with_elo(500, 500, 1)
        assert (game.black_win_probability() > 0.5)

    def test_higher_rank_should_confer_advantage(self):
        game = self.setup_game_with_elo(600, 500, 0)
        assert (game.white_win_probability() > 0.5)

    def test_winrates_are_equal_for_same_elo_delta(self):
        game = self.setup_game_with_elo(100, 200, 0)
        game2 = self.setup_game_with_elo(200, 300, 0)
        assert (abs(game.white_win_probability() -
                    game2.white_win_probability()) < 0.0001)

    def test_winrates_for_twice_as_strong_player(self):
        game = self.setup_game_with_elo(100, 200, 0)
        assert (abs(0.359935 - game.white_win_probability()) < 0.0001)

    def test_winrates_should_be_inversely_proportional_with_unequal_ranks(
            self):
        game = self.setup_game_with_elo(600, 500, 0)
        assert (game.white_win_probability() -
                (1 - game.black_win_probability()) < 0.0001)

    def test_winrates_should_be_inversely_proportional_with_handicap(self):
        game = self.setup_game_with_elo(500, 500, 4)
        assert (game.white_win_probability() -
                (1 - game.black_win_probability()) < 0.0001)

    def test_output(self):
        self.whr.create_game("shusaku", "shusai", "B", 1, 0)
        self.whr.create_game("shusaku", "shusai", "W", 2, 0)
        self.whr.create_game("shusaku", "shusai", "W", 3, 0)
        self.whr.create_game("shusaku", "shusai", "W", 4, 0)
        self.whr.create_game("shusaku", "shusai", "W", 4, 0)
        self.whr.iterate(50)
        list(map(lambda x: list(map(round, x)), [[0.9]]))
        assert ([[1, -92, 71], [2, -94, 71], [3, -95, 71],
                 [4, -96, 72]] == list(
                     map(lambda x: list(map(round, x)),
                         self.whr.ratings_for_player("shusaku"))))
        assert ([[1, 92, 71], [2, 94, 71], [3, 95, 71], [4, 96, 72]] == list(
            map(lambda x: list(map(round, x)),
                self.whr.ratings_for_player("shusai"))))

    def test_unstable_exception_raised_in_certain_cases(self):
        for i in range(10):
            self.whr.create_game("anchor", "player", "B", 1, 0)
            self.whr.create_game("anchor", "player", "W", 1, 0)
        for i in range(10):
            self.whr.create_game("anchor", "player", "B", 180, 600)
            self.whr.create_game("anchor", "player", "W", 180, 600)
        raises_exception = False
        try:
            self.whr.iterate(10)
        except whr.UnstableRatingException:
            raises_exception = True
        assert (raises_exception)


if __name__ == '__main__':
    whrt = WholeHistoryRatingTest()
    whrt.test_even_game_between_equal_strength_players_should_have_white_winrate_of_50_percent(
    )
    whrt.test_handicap_should_confer_advantage()
    whrt.test_higher_rank_should_confer_advantage()
    whrt.test_winrates_are_equal_for_same_elo_delta()
    whrt.test_winrates_for_twice_as_strong_player()
    whrt.test_winrates_should_be_inversely_proportional_with_unequal_ranks()
    whrt.test_winrates_should_be_inversely_proportional_with_handicap()
    whrt.test_output()
    whrt.test_unstable_exception_raised_in_certain_cases()
