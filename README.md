Whole History Rating
====================

|      CI              | status |
|----------------------|--------|
| conda.recipe         | [![Conda Actions Status][actions-conda-badge]][actions-conda-link] |
| pip builds           | [![Pip Actions Status][actions-pip-badge]][actions-pip-link] |
| cibuildwheel   | [![Wheels Actions Status][actions-wheels-badge]][actions-wheels-link] |

[actions-conda-link]:      https://github.com/wind23/whole_history_rating/actions?query=workflow%3AConda
[actions-conda-badge]:     https://github.com/wind23/whole_history_rating/workflows/Conda/badge.svg
[actions-pip-link]:        https://github.com/wind23/whole_history_rating/actions?query=workflow%3APip
[actions-pip-badge]:       https://github.com/wind23/whole_history_rating/workflows/Pip/badge.svg
[actions-wheels-link]:     https://github.com/wind23/whole_history_rating/actions?query=workflow%3AWheels
[actions-wheels-badge]:    https://github.com/wind23/whole_history_rating/workflows/Wheels/badge.svg

## Description

A Python interface incorporating a C++ implementation of the [Whole History Rating](http://remi.coulom.free.fr/WHR/WHR.pdf) algorithm proposed by [Rémi Coulom](http://remi.coulom.free.fr/).

The implementation is based on the [Ruby code](https://github.com/goshrine/whole_history_rating) of [GoShrine](http://goshrine.com).

## Installation

To install it from PyPI:

    pip install whr

To install it from source code:

    git clone git@github.com:wind23/whole_history_rating.git
    pip install ./whole_history_rating

To build this package from the source code, you will need a recent version of Python 3 installed, along with `setuptools>=42` and `pybind11>=2.10.0`. Furthermore, depending on your operating system, you may also require the installation of the appropriate C++ build environment. If you are uncertain about the required dependencies, you can begin by attempting `pip install` and follow the instructions provided by your system to install the necessary components.

If you encounter compatibility issues while using the latest version, you can also try the older version implemented purely in Python:

    pip install whr==1.0.1

## Usage

Here is an easy example about how to use the package:

	In [1]: import whr
	   ...: import math
	   ...:
	   ...: base = whr.Base(config={"w2": 30})
	   ...: base.create_game("Alice", "Carol", "D", 0)  # Alice and Carol had a draw on Day 0
	   ...: base.create_game("Bob", "Dave", "B", 10)  # Bob won Dave on Day 10
	   ...: base.create_game("Dave", "Alice", "W", 30)  # Dave lost to Alice on Day 30
	   ...: base.create_game("Bob", "Carol", "W", 60)  # Bob lost to Carol on Day 60
	   ...:
	   ...: base.iterate(50)  # iterate for 50 rounds

	In [2]: print(base.ratings_for_player("Alice"))
	   ...: print(base.ratings_for_player("Bob"))
	   ...: print(base.ratings_for_player("Carol"))
	   ...: print(base.ratings_for_player("Dave"))
	[[0, 78.50976252870765, 185.55230942797314], [30, 79.47183295485291, 187.12327376311526]]
	[[10, -15.262552175731392, 180.95086989932025], [60, -18.086030877782818, 183.0820052639819]]
	[[0, 103.91877749030998, 180.55812567296852], [60, 107.30695193277168, 183.1250043094528]]
	[[10, -176.67739359273045, 201.15282077913983], [30, -177.3187738768273, 202.03179750776144]]

	In [3]: print(base.get_ordered_ratings())
	[('Carol', [[0, 103.91877749030998, 180.55812567296852], [60, 107.30695193277168, 183.1250043094528]]), ('Alice', [[0, 78.50976252870765, 185.55230942797314], [30, 79.47183295485291, 187.12327376311526]]), ('Bob', [[10, -15.262552175731392, 180.95086989932025], [60, -18.086030877782818, 183.0820052639819]]), ('Dave', [[10, -176.67739359273045, 201.15282077913983], [30, -177.3187738768273, 202.03179750776144]])]

	In [4]: evaluate = whr.Evaluate(base)
	   ...: test_games = [
	   ...:     ["Alice", "Bob", "B", 0],
	   ...:     ["Bob", "Carol", "W", 20],
	   ...:     ["Dave", "Bob", "D", 50],
	   ...:     ["Alice", "Dave", "B", 70],
	   ...: ]
	   ...: log_likelihood = evaluate.evaluate_ave_log_likelihood_games(test_games)

	In [5]: print("Likelihood: ", math.exp(log_likelihood))
	Likelihood:  0.6274093351974668

To learn more about the detailed usage, please refer to the docstrings of [`whr.Base`](https://github.com/wind23/whole_history_rating/blob/master/whr/base.py) and [`whr.Evaluate`](https://github.com/wind23/whole_history_rating/blob/master/whr/evaluate.py).

## References

Rémi Coulom. [Whole-history rating: A Bayesian rating system for players of time-varying strength](https://www.remi-coulom.fr/WHR/WHR.pdf). In _International Conference on Computers and Games_. 2008.
