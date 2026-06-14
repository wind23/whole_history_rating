import pytest
import whr

def test_base_initialization():
    # Test default initialization
    base = whr.Base()
    assert base.core is not None

    # Test initialization with custom config dict
    config = {"w2": 250.0, "virtual_games": 3}
    base_custom = whr.Base(config=config)
    
    # Test initialization with keyword arguments
    base_kwargs = whr.Base(w2=100.0, virtual_games=4)


def test_rating_outputs():
    base = whr.Base()
    # Adding games
    base.create_game("shusaku", "shusai", "B", 1, 0)
    base.create_game("shusaku", "shusai", "W", 2, 0)
    base.create_game("shusaku", "shusai", "W", 3, 0)
    base.create_game("shusaku", "shusai", "W", 4, 0)
    base.create_game("shusaku", "shusai", "W", 4, 0)
    
    base.iterate(50)
    
    shusaku_ratings = list(map(lambda x: list(map(round, x)), base.ratings_for_player("shusaku")))
    shusai_ratings = list(map(lambda x: list(map(round, x)), base.ratings_for_player("shusai")))
    
    assert shusaku_ratings == [[1, -92, 147], [2, -94, 147], [3, -95, 147], [4, -96, 147]]
    assert shusai_ratings == [[1, 92, 147], [2, 94, 147], [3, 95, 147], [4, 96, 147]]


def test_game_order_independence():
    whr1 = whr.Base()
    whr1.create_game("alice", "bob", "W", 1, 0)
    whr1.create_game("alice", "bob", "B", 2, 0)
    whr1.create_game("alice", "bob", "W", 3, 0)
    whr1.iterate(50)

    whr2 = whr.Base()
    whr2.create_game("alice", "bob", "W", 3, 0)
    whr2.create_game("alice", "bob", "B", 2, 0)
    whr2.create_game("alice", "bob", "W", 1, 0)
    whr2.iterate(50)

    ratings1_alice = sorted(whr1.ratings_for_player("alice"), key=lambda x: x[0])
    ratings2_alice = sorted(whr2.ratings_for_player("alice"), key=lambda x: x[0])
    ratings1_bob = sorted(whr1.ratings_for_player("bob"), key=lambda x: x[0])
    ratings2_bob = sorted(whr2.ratings_for_player("bob"), key=lambda x: x[0])

    assert ratings1_alice == ratings2_alice
    assert ratings1_bob == ratings2_bob


def test_self_play_check():
    base = whr.Base()
    # base.create_game handles player names equality in C++ setup_game, prints std::cerr and returns nullptr.
    # In python, we should make sure it doesn't crash the program.
    base.create_game("alice", "alice", "W", 1, 0)
    assert len(base.ratings_for_player("alice")) == 0


def test_iterate_until_converge():
    base = whr.Base()
    base.create_game("alice", "bob", "W", 1, 0)
    base.create_game("alice", "bob", "B", 2, 0)
    base.create_game("alice", "bob", "W", 3, 0)
    
    # Should run and terminate
    iterations = base.iterate_until_converge(verbose=False)
    assert iterations > 0
    
    ratings_alice = base.ratings_for_player("alice")
    assert len(ratings_alice) == 3


def test_get_ordered_ratings():
    base = whr.Base()
    base.create_game("alice", "bob", "W", 1, 0)
    base.create_game("alice", "bob", "B", 2, 0)
    base.iterate(10)
    
    ordered = base.get_ordered_ratings()
    assert len(ordered) == 2
    # Verify tuple structure [player_name, ratings_list]
    assert ordered[0][0] in {"alice", "bob"}
    assert isinstance(ordered[0][1], list)
