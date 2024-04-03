import math
from typing import Union
import whr_core
from .base import Base


class Evaluate:
    def __init__(self, base: Base):
        """
        Tool to evaluate the performance the trained model of Elo ratings.

        Parameters
        ----------
        base : Base
            Trained model of Elo ratings.
        """
        self.core = whr_core.Evaluate(base.core)

    def get_rating(
        self, name: str, time_step: int, ignore_null_players: bool = True
    ) -> Union[float, None]:
        """
        Get the rating of a particular player at a particular time step.

        Parameters
        ----------
        name : str
            Name of the player.

        time_step : int
            Time step of the player.

        ignore_null_players : bool, default = True
            Ignore players not appearing in the database.
            If True, rating of null players will be set to None.
            If False, rating of null players will be set to 0.

        Returns
        -------
        float or None
            Rating of the requested player at the requested time step.
        """
        ret = self.core.get_rating(name, time_step, ignore_null_players)
        if not math.isfinite(ret):
            return None
        return ret

    def evaluate_ave_log_likelihood_games(
        self, games: list, ignore_null_players: bool = True
    ) -> float:
        """
        Compute the average log likelihood for the test dataset,
        which is a list of games.

        Parameters
        ----------
        games : list
            A list of games as the test dataset.
        Example:
        ```
        [['Alice', 'Carol', 'D', 0],
         ['Bob', 'Dave', 'B', 10],
         ['Dave', 'Alice', 'W', 30, 10.],
         ['Bob', 'Carol', 'W', 60, 20.]]
         ```

        ignore_null_players : bool, optional
            Ignore players not appearing in the database.
            For each game, if there is a player not appearing the database,
            it will not be counted in the average log likelihood.

        Returns
        -------
        float
            Average log likelihood for the test dataset.
        """
        return self.core.evaluate_ave_log_likelihood_games(games, ignore_null_players)
