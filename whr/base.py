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
        return self.core.iterate_until_converge(verbose)

    def iterate(self, count: int):
        """
        Iterate the computation for a fixed number of rounds.

        Parameters
        ----------
        count : int
            Number of rounds.
        """
        self.core.iterate(count)

    def load_csv(self, filepath_or_buffer):
        """
        Load games from a CSV file or file-like buffer.

        Parameters
        ----------
        filepath_or_buffer : str, Path, or file-like object
            The path to the CSV file or a file-like buffer containing CSV data.
        """
        import csv
        import io
        import warnings

        # Open file if path-like is provided
        close_file = False
        if isinstance(filepath_or_buffer, str):
            f = open(filepath_or_buffer, "r", encoding="utf-8", newline="")
            close_file = True
        elif hasattr(filepath_or_buffer, "read"):
            f = filepath_or_buffer
        else:
            f = open(filepath_or_buffer, "r", encoding="utf-8", newline="")
            close_file = True

        try:
            reader = csv.reader(f)
            rows = []
            for r in reader:
                # Skip empty rows or header-less blanks
                if not r or all(cell.strip() == "" for cell in r):
                    continue
                rows.append([cell.strip() for cell in r])

            if not rows:
                warnings.warn("The CSV file is empty.", UserWarning)
                return

            header_row = rows[0]

            black_aliases = {"black", "black_player", "player_black", "p1", "player1", "black player"}
            white_aliases = {"white", "white_player", "player_white", "p2", "player2", "white player"}
            winner_aliases = {"winner", "result", "outcome", "win", "winner_player", "victor"}
            time_step_aliases = {"time_step", "time", "step", "day", "date", "round"}
            handicap_aliases = {"handicap", "advantage", "komi"}

            black_idx = None
            white_idx = None
            winner_idx = None
            time_step_idx = None
            handicap_idx = None

            # Check if first row is a header
            is_header = False
            for idx, col in enumerate(header_row):
                col_lower = col.lower()
                if col_lower in black_aliases:
                    black_idx = idx
                    is_header = True
                elif col_lower in white_aliases:
                    white_idx = idx
                    is_header = True
                elif col_lower in winner_aliases:
                    winner_idx = idx
                    is_header = True
                elif col_lower in time_step_aliases:
                    time_step_idx = idx
                    is_header = True
                elif col_lower in handicap_aliases:
                    handicap_idx = idx
                    is_header = True

            if is_header:
                data_rows = rows[1:]
                missing_headers = []
                if black_idx is None: missing_headers.append("black")
                if white_idx is None: missing_headers.append("white")
                if winner_idx is None: missing_headers.append("winner")
                if time_step_idx is None: missing_headers.append("time_step")

                if missing_headers:
                    warnings.warn(
                        f"Missing headers: {', '.join(missing_headers)}. Attempting to match by positional fallback.",
                        UserWarning
                    )
                    if black_idx is None and len(header_row) > 0: black_idx = 0
                    if white_idx is None and len(header_row) > 1: white_idx = 1
                    if winner_idx is None and len(header_row) > 2: winner_idx = 2
                    if time_step_idx is None and len(header_row) > 3: time_step_idx = 3
                    if handicap_idx is None and len(header_row) > 4: handicap_idx = 4
            else:
                warnings.warn(
                    "No CSV header detected. Falling back to default column order: "
                    "black_player, white_player, winner, time_step, handicap.",
                    UserWarning
                )
                data_rows = rows
                black_idx = 0 if len(header_row) > 0 else None
                white_idx = 1 if len(header_row) > 1 else None
                winner_idx = 2 if len(header_row) > 2 else None
                time_step_idx = 3 if len(header_row) > 3 else None
                handicap_idx = 4 if len(header_row) > 4 else None

            # Process games
            for row_num, row in enumerate(data_rows, start=2 if is_header else 1):
                def get_val(idx, default=None):
                    if idx is not None and idx < len(row):
                        return row[idx]
                    return default

                black_val = get_val(black_idx)
                white_val = get_val(white_idx)
                winner_raw = get_val(winner_idx)
                time_step_raw = get_val(time_step_idx)
                handicap_raw = get_val(handicap_idx)

                # Skip and warn on empty/missing player names
                if not black_val or not white_val:
                    warnings.warn(
                        f"Row {row_num}: Missing player name(s). Skipping game.",
                        UserWarning
                    )
                    continue

                if black_val == white_val:
                    warnings.warn(
                        f"Row {row_num}: Self-play detected ({black_val} vs {white_val}). Skipping game.",
                        UserWarning
                    )
                    continue

                # Winner normalization
                winner = "D"
                if winner_raw is not None and winner_raw.strip() != "":
                    winner_clean = winner_raw.strip().lower()
                    if winner_clean in {"b", "black", "1-0", "1", "black win"}:
                        winner = "B"
                    elif winner_clean in {"w", "white", "0-1", "0", "white win"}:
                        winner = "W"
                    elif winner_clean in {"d", "draw", "1/2-1/2", "0.5"}:
                        winner = "D"
                    else:
                        warnings.warn(
                            f"Row {row_num}: Invalid winner '{winner_raw}'. Defaulting to Draw ('D').",
                            UserWarning
                        )
                        winner = "D"
                else:
                    warnings.warn(
                        f"Row {row_num}: Missing winner. Defaulting to Draw ('D').",
                        UserWarning
                    )
                    winner = "D"

                # Time step parsing
                time_step = 0
                if time_step_raw is not None and time_step_raw.strip() != "":
                    try:
                        time_step = int(round(float(time_step_raw)))
                    except ValueError:
                        warnings.warn(
                            f"Row {row_num}: Invalid time_step '{time_step_raw}'. Defaulting to 0.",
                            UserWarning
                        )
                        time_step = 0
                else:
                    warnings.warn(
                        f"Row {row_num}: Missing time_step. Defaulting to 0.",
                        UserWarning
                    )
                    time_step = 0

                # Handicap parsing
                handicap = 0.0
                if handicap_raw is not None and handicap_raw.strip() != "":
                    try:
                        handicap = float(handicap_raw)
                    except ValueError:
                        warnings.warn(
                            f"Row {row_num}: Invalid handicap '{handicap_raw}'. Defaulting to 0.0.",
                            UserWarning
                        )
                        handicap = 0.0

                self.create_game(black_val, white_val, winner, time_step, handicap)

        finally:
            if close_file:
                f.close()
