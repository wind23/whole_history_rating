# Whole History Rating

## Description

A Python implementation of the [Whole History Rating](http://remi.coulom.free.fr/WHR/WHR.pdf) algorithm proposed by [Rémi Coulom](http://remi.coulom.free.fr/).

The implementation is based on the [Ruby code](https://github.com/goshrine/whole_history_rating) of [GoShrine](http://goshrine.com).

## Installation

    pip install whr

# Usage

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

# References

Rémi Coulom. Whole-history rating: A Bayesian rating system for players of time-varying strength. In _International Conference on Computers and Games_. 2008. <https://www.remi-coulom.fr/WHR/WHR.pdf>
