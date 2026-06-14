# Whole History Rating (WHR)

[![Conda Actions Status](https://github.com/wind23/whole_history_rating/workflows/Conda/badge.svg)](https://github.com/wind23/whole_history_rating/actions?query=workflow%3AConda)
[![Pip Actions Status](https://github.com/wind23/whole_history_rating/workflows/Pip/badge.svg)](https://github.com/wind23/whole_history_rating/actions?query=workflow%3APip)
[![Wheels Actions Status](https://github.com/wind23/whole_history_rating/workflows/Wheels/badge.svg)](https://github.com/wind23/whole_history_rating/actions?query=workflow%3AWheels)

A Python interface incorporating a highly optimized C++ implementation of the [Whole History Rating (WHR)](http://remi.coulom.free.fr/WHR/WHR.pdf) algorithm proposed by [Rémi Coulom](http://remi.coulom.free.fr/). WHR computes time-varying Elo ratings for players of games (e.g., Chess, Go) by optimizing the log-likelihood of all game results across history simultaneously.

This C++ implementation is based on the [Ruby implementation](https://github.com/goshrine/whole_history_rating) by [GoShrine](http://goshrine.com).

---

## Features

- **Blazing Fast**: The core algorithm is implemented in C++ (via `pybind11`), allowing it to scale to tens of thousands of games.
- **Tolerant CSV Loading**: Built-in support to ingest games from CSV files with smart header alias matching, winner normalization, and graceful handling of missing or malformed fields.
- **Robust Evaluation**: Standardized validation metrics including average log-likelihood computation.
- **Highly Configurable**: Custom rating volatility parameter ($w^2$) and virtual game regularization.

---

## Installation

### From PyPI
```bash
pip install whr
```

### From Source
```bash
git clone https://github.com/wind23/whole_history_rating.git
cd whole_history_rating
pip install .
```

> **Note**: Building from source requires a C++ compiler supporting C++11 (GCC, Clang, MSVC) and the `pybind11` package.

---

## Usage

### 1. Basic API Usage

```python
import whr
import math

# Initialize the rating database with volatility parameter w^2 = 30
base = whr.Base(config={"w2": 30})

# Create game records manually:
# create_game(black_player, white_player, winner, time_step, handicap=0.0)
# Winner options: "B" (black wins), "W" (white wins), "D" (draw)
base.create_game("Alice", "Carol", "D", 0)   # Day 0: Draw
base.create_game("Bob", "Dave", "B", 10)     # Day 10: Bob won
base.create_game("Dave", "Alice", "W", 30)   # Day 30: Alice won (Dave lost)
base.create_game("Bob", "Carol", "W", 60)    # Day 60: Carol won (Bob lost)

# Run 50 Newton-Raphson iterations to solve for player ratings
base.iterate(50)

# Retrieve rating history for individual players: returns list of [day, elo, uncertainty]
print("Alice ratings:", base.ratings_for_player("Alice"))
# Output: [[0, 78.51, 185.55], [30, 79.47, 187.12]]

# Get all player ratings sorted by final strength
print("Ordered ratings:", base.get_ordered_ratings())
```

### 2. Loading Games from CSV

The `load_csv()` method enables importing games from a CSV file or file-like buffer. It is designed to be highly tolerant of formatting errors:

```python
import whr
import io

base = whr.Base()

csv_content = """
black_player, white_player, winner, time_step, handicap
Alice, Bob, B, 1, 0.0
Bob, Carol, W, 2, 0.0
Carol, Alice, D, 3, 5.0
"""

# Load from a file path or a StringIO buffer
base.load_csv(io.StringIO(csv_content))
base.iterate(50)
```

#### CSV Format & Column Aliases
WHR searches the header row case-insensitively for matches using the following aliases:

| Logical Column | Accepted Header Aliases | Default Fallback / Behavior |
| :--- | :--- | :--- |
| **Black Player** | `black`, `black_player`, `player_black`, `p1`, `player1`, `black player` | Row is skipped if missing/empty. |
| **White Player** | `white`, `white_player`, `player_white`, `p2`, `player2`, `white player` | Row is skipped if missing/empty. |
| **Winner** | `winner`, `result`, `outcome`, `win`, `winner_player`, `victor` | Defaults to a Draw (`D`) with a warning. |
| **Time Step** | `time_step`, `time`, `step`, `day`, `date`, `round` | Defaults to `0` with a warning. |
| **Handicap** | `handicap`, `advantage`, `komi` | Defaults to `0.0` (no warning if absent, warning if invalid). |

#### Winner Normalization Rules
WHR normalizes various winner representations to simplify integration:
- **Black Win**: `B`, `black`, `b`, `1-0`, `1`, `black win`
- **White Win**: `W`, `white`, `w`, `0-1`, `0`, `white win`
- **Draw**: `D`, `draw`, `d`, `1/2-1/2`, `0.5`
- *Any unrecognized string defaults to a Draw (`D`) with a warning.*

#### Tolerance & Warning Behavior
If the CSV structure contains minor anomalies, the parser emits a `UserWarning` instead of failing:
- **Missing Headers**: If headers cannot be detected at all, WHR falls back to treating columns positionally as `[black, white, winner, time_step, handicap]`.
- **Invalid Numbers**: If `time_step` or `handicap` is non-numeric, it is defaulted to `0` or `0.0` respectively, and a warning is logged.
- **Float Time Steps**: If the `time_step` contains decimals, it is safely rounded to the nearest integer.
- **Empty & Comment Lines**: Empty lines and clean space rows are skipped silently.

---

## API Reference

### `whr.Base`

Main interface for calculating ratings.

- `__init__(config=None, w2=300.0, virtual_games=2)`
  - `config`: Optional dict containing `w2` and `virtual_games`.
  - `w2`: Rating variance parameter controlling how fast rating changes over time (default: 300.0).
  - `virtual_games`: Number of virtual draw games assigned to players on their first day for rating regularization.
- `create_game(black, white, winner, time_step, handicap=0.0)`: Create and register a single game.
- `create_games(games)`: Ingest a list of games in the format `[black, white, winner, time_step, handicap]`.
- `load_csv(filepath_or_buffer)`: Load games from a CSV file path or file-like buffer.
- `iterate(count)`: Perform a fixed number of Newton-Raphson optimization steps.
- `iterate_until_converge(verbose=True)`: Iterate until convergence. Returns the total number of iterations.
- `ratings_for_player(name)`: Get the rating timeline of a player as `[[day, rating, uncertainty], ...]`.
- `get_ordered_ratings()`: Get sorted ratings for all active players.
- `log_likelihood()`: Returns the overall log-likelihood score of the current model.

### `whr.Evaluate`

Evaluates rating predictability on external test datasets.

- `__init__(base)`: Initialize with a trained `whr.Base` rating database.
- `get_rating(name, time_step, ignore_null_players=True)`: Get the rating of a player on a specific day.
- `evaluate_ave_log_likelihood_games(games, ignore_null_players=True)`: Compute average log-likelihood across a list of test games.

---

## Running Tests

Test files are modularized and cover base functionality, evaluation metrics, and CSV parsing:

```bash
python -m pytest tests/
```

To run with verbose output:

```bash
python -m pytest tests/ -v
```

---

## References

Rémi Coulom. [Whole-history rating: A Bayesian rating system for players of time-varying strength](https://www.remi-coulom.fr/WHR/WHR.pdf). In _International Conference on Computers and Games_. 2008.
