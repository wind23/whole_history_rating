import whr_core


__version__ = whr_core.__version__


class Base:
    def __init__(self, config: dict = None, w2: float = 300.0, virtual_games: int = 2):
        """
        Fundamental database for computing whole-history rating (WHR).

        Parameters
        ----------
        config : dict, default = None
            Config for setting the parameters for Base.
            Example: config = {"w2": w2, "virtual_games": virtual_games}
            If config is unset, the parameters `w2` and `virtual_games` will be used.

        w2 : float, default = 300.0
            The parameter of w^2 described in the paper of Rémi Coulom,
            where w indicates the variability of ratings in time.
            This parameter is ineffective when `config["w2"]` is set.

        virtual_games : int, default = 2
            Number of virtual draw games assigned to player on the first day.
            This parameter is ineffective when `config["virtual_games"]` is set.

        Example
        -------
        ```
        import whr

        base = whr.Base(config={'w2': 30})
        base.create_game('Alice', 'Carol', 'D', 0) # Alice and Carol had a draw on Day 0
        base.create_game('Bob', 'Dave', 'B', 10)   # Bob won Dave on Day 10
        base.create_game('Dave', 'Alice', 'W', 30) # Dave lost to Alice on Day 30
        base.create_game('Bob', 'Carol', 'W', 60)  # Bob lost to Carol on Day 60

        base.iterate(50)                           # iterate for 50 rounds

        print(base.ratings_for_player('Alice'))
        print(base.ratings_for_player('Bob'))
        print(base.ratings_for_player('Carol'))
        print(base.ratings_for_player('Dave'))

        print(base.get_ordered_ratings())
        ```

        Output:
        ```
        [[0, 78.50976252870765, 185.55230942797314], [30, 79.47183295485291, 187.12327376311526]]
        [[10, -15.262552175731392, 180.95086989932025], [60, -18.086030877782818, 183.0820052639819]]
        [[0, 103.91877749030998, 180.55812567296852], [60, 107.30695193277168, 183.1250043094528]]
        [[10, -176.67739359273045, 201.15282077913983], [30, -177.3187738768273, 202.03179750776144]]
        [('Carol', [[0, 103.91877749030998, 180.55812567296852], [60, 107.30695193277168, 183.1250043094528]]),
         ('Alice', [[0, 78.50976252870765, 185.55230942797314], [30, 79.47183295485291, 187.12327376311526]]),
         ('Bob', [[10, -15.262552175731392, 180.95086989932025], [60, -18.086030877782818, 183.0820052639819]]),
         ('Dave', [[10, -176.67739359273045, 201.15282077913983], [30, -177.3187738768273, 202.03179750776144]])]
        """
        if config is not None:
            if "w2" in config:
                w2 = config["w2"]
            if "virtual_games" in config:
                virtual_games = config["virtual_games"]
        self.core = whr_core.Base(w2, virtual_games)

    def print_ordered_ratings(self):
        """
        Print the ordered ratings of all players during the whole history.
        """
        self.core.print_ordered_ratings()

    def get_ordered_ratings(self) -> list:
        """
        Get the ordered ratings of all players during the whole history.

        Returns
        -------
        list
            A list of [time_step, elo, uncertainty] for all players in all days.
            The uncertainty is shown as the standard deviation of Elo.
        Example:
        ```
        [('Carol', [[0, 103.91877749030998, 180.55812567296852], [60, 107.30695193277168, 183.1250043094528]]),
         ('Alice', [[0, 78.50976252870765, 185.55230942797314], [30, 79.47183295485291, 187.12327376311526]]),
         ('Bob', [[10, -15.262552175731392, 180.95086989932025], [60, -18.086030877782818, 183.0820052639819]]),
         ('Dave', [[10, -176.67739359273045, 201.15282077913983], [30, -177.3187738768273, 202.03179750776144]])]
        """
        return self.core.get_ordered_ratings()

    def log_likelihood(self) -> float:
        """
        Compute the log likehihood for all games in the database.

        Returns
        -------
        float
            The computed log likelihood for all games.
        """
        return self.core.log_likelihood()

    def ratings_for_player(self, name: str) -> list:
        """
        Get the rating for a player based on the player name.

        Parameters
        ----------
        name : str
            Name of the requested player.

        Returns
        -------
        list
            A list of [time_step, elo, uncertainty] for the requested player in all days.
        Example:
        ```
        [[0, 103.91877749030998, 180.55812567296852], [60, 107.30695193277168, 183.1250043094528]]
        """
        return self.core.ratings_for_player(name)

    def create_games(self, games: list):
        """
        Create a list of games, inserting the games and related players into the database.

        Parameters
        ----------
        games : list
            List of games, each element of which has the form:
            [black, white, winner, time_step, handicap (optional)]
        Example:
        ```
        [['Alice', 'Carol', 'D', 0],
         ['Bob', 'Dave', 'B', 10],
         ['Dave', 'Alice', 'W', 30, 10.],
         ['Bob', 'Carol', 'W', 60, 20.]]
        ```
        """
        self.core.create_games(games)

    def create_game(
        self, black: str, white: str, winner: str, time_step: int, handicap: float = 0.0
    ):
        """
        Create a game, inserting the game and related players into the database.

        Parameters
        ----------
        black : str
            Name of the black player.

        white : str
            Name of the white player.

        winner : str, {"B", "W", "D"}
            Winner of the game: black wins, white wins, or draw.

        time_step : int
            Time step (day) of the game.

        handicap : float, default = 0.0
            The advantage of black (by Elo) of the game by default.
        """
        self.core.create_game(black, white, winner, time_step, handicap)

    def iterate_until_converge(self, verbose: bool = True):
        """
        Iterate the computation until the ratings converge.
        The ratings are considered to have converged
        when the Elo rating of no player is updated within the percentile after 10 rounds.

        Parameters
        ----------
        verbose : bool, default = True
            Printing iteration information after each round.
        """
        self.core.iterate_until_converge(verbose)

    def iterate(self, count: int):
        """
        Iterate the computation for a fixed number of rounds.

        Parameters
        ----------
        count : int
            Number of rounds.
        """
        self.core.iterate(count)
