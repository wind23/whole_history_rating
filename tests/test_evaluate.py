import pytest
import whr

def test_evaluate_ave_log_likelihood():
    base = whr.Base()
    base.create_game("shusaku", "shusai", "B", 1, 0)
    base.create_game("shusaku", "shusai", "W", 2, 0)
    base.create_game("shusaku", "shusai", "W", 3, 0)
    base.create_game("shusaku", "shusai", "W", 4, 0)
    base.create_game("shusaku", "shusai", "W", 4, 0)
    base.iterate(50)

    test_games = [
        ["shusaku", "shusai", "B", 1],
        ["shusaku", "shusai", "W", 2],
        ["shusaku", "shusai", "W", 3, 0],
        ["shusaku", "shusai", "W", 4, 0],
        ["shusaku", "shusai", "W", 4, 0],
    ]
    
    evaluate = whr.Evaluate(base)
    test_log_likelihood = evaluate.evaluate_ave_log_likelihood_games(test_games)
    assert round(test_log_likelihood * 100000) == -50215
