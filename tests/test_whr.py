import whr


class WholeHistoryRatingTest:
    def __init__(self):
        self.whr = whr.Base()

    def test_output(self):
        self.whr.create_game("shusaku", "shusai", "B", 1, 0)
        self.whr.create_game("shusaku", "shusai", "W", 2, 0)
        self.whr.create_game("shusaku", "shusai", "W", 3, 0)
        self.whr.create_game("shusaku", "shusai", "W", 4, 0)
        self.whr.create_game("shusaku", "shusai", "W", 4, 0)
        self.whr.iterate(50)
        list(map(lambda x: list(map(round, x)), [[0.9]]))
        assert [[1, -92, 147], [2, -94, 147], [3, -95, 147], [4, -96, 147]] == list(
            map(lambda x: list(map(round, x)), self.whr.ratings_for_player("shusaku"))
        )
        assert [[1, 92, 147], [2, 94, 147], [3, 95, 147], [4, 96, 147]] == list(
            map(lambda x: list(map(round, x)), self.whr.ratings_for_player("shusai"))
        )

    def test_evaluate(self):
        test_games = [
            ["shusaku", "shusai", "B", 1],
            ["shusaku", "shusai", "W", 2],
            ["shusaku", "shusai", "W", 3, 0],
            ["shusaku", "shusai", "W", 4, 0],
            ["shusaku", "shusai", "W", 4, 0],
        ]
        evaluate = whr.Evaluate(self.whr)
        test_log_likelihood = evaluate.evaluate_ave_log_likelihood_games(test_games)
        assert round(test_log_likelihood * 100000) == -50215


def test_whr_class():
    whrt = WholeHistoryRatingTest()
    whrt.test_output()
    whrt.test_evaluate()


if __name__ == "__main__":
    test_whr_class()
