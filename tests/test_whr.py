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
        assert [[1, -92, 71], [2, -94, 71], [3, -95, 71], [4, -96, 72]] == list(
            map(lambda x: list(map(round, x)), self.whr.ratings_for_player("shusaku"))
        )
        assert [[1, 92, 71], [2, 94, 71], [3, 95, 71], [4, 96, 72]] == list(
            map(lambda x: list(map(round, x)), self.whr.ratings_for_player("shusai"))
        )


def test_whr_class():
    whrt = WholeHistoryRatingTest()
    whrt.test_output()


if __name__ == "__main__":
    test_whr_class()
