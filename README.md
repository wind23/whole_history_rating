Whole History Rating
====================

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
    ...:
    ...: base = whr.Base(config={'w2': 30})
    ...: base.create_game('Alice', 'Carol', 'D', 0) # Alice and Carol had a draw on Day 0
    ...: base.create_game('Bob', 'Dave', 'B', 10)   # Bob won Dave on Day 10
    ...: base.create_game('Dave', 'Alice', 'W', 30) # Dave lost to Alice on Day 30
    ...: base.create_game('Bob', 'Carol', 'W', 60)  # Bob lost to Carol on Day 60
    ...:
    ...: base.iterate(50)                           # iterate for 50 rounds

    In [2]: print(base.ratings_for_player('Alice'))
    ...: print(base.ratings_for_player('Bob'))
    ...: print(base.ratings_for_player('Carol'))
    ...: print(base.ratings_for_player('Dave'))
    [[0, 78.50976252870765, 114.0890917675107], [30, 79.47183295485291, 116.02912272478814]]
    [[10, -15.262552175731381, 108.50075126605397], [60, -18.08603087778281, 111.07152016073245]]
    [[0, 103.9187774903099, 108.03027219107216], [60, 107.30695193277161, 111.12369929419124]]
    [[10, -176.6773935927304, 134.07989121465133], [30, -177.31877387682724, 135.25422816732765]]

    In [3]: print(base.get_ordered_ratings())
    [('Carol', [[0, 103.9187774903099, 108.03027219107216], [60, 107.30695193277161, 111.12369929419124]]), ('Alice', [[0, 78.50976252870765, 114.0890917675107], [30, 79.47183295485291, 116.02912272478814]]), ('Bob', [[10, -15.262552175731381, 108.50075126605397], [60, -18.08603087778281, 111.07152016073245]]), ('Dave', [[10, -176.6773935927304, 134.07989121465133], [30, -177.31877387682724, 135.25422816732765]])]

To learn more about the detailed usage, please refer to the docstrings of `whr.Base` and `whr.Evaluate`.

## References

Rémi Coulom. [Whole-history rating: A Bayesian rating system for players of time-varying strength](https://www.remi-coulom.fr/WHR/WHR.pdf). In _International Conference on Computers and Games_. 2008.
