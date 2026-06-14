import io
import warnings
import pytest
import whr

def test_load_csv_standard():
    base = whr.Base()
    csv_data = """black_player,white_player,winner,time_step,handicap
Alice,Carol,D,0,0.0
Bob,Dave,B,10,0.0
Dave,Alice,W,30,10.0
"""
    f = io.StringIO(csv_data)
    
    # Standard load should not raise warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        base.load_csv(f)

    # Verify players and games were created
    alice_ratings = base.ratings_for_player("Alice")
    bob_ratings = base.ratings_for_player("Bob")
    carol_ratings = base.ratings_for_player("Carol")
    dave_ratings = base.ratings_for_player("Dave")

    assert len(alice_ratings) == 2  # day 0 (vs Carol), day 30 (vs Dave)
    assert len(bob_ratings) == 1    # day 10 (vs Dave)
    assert len(carol_ratings) == 1  # day 0 (vs Alice)
    assert len(dave_ratings) == 2   # day 10 (vs Bob), day 30 (vs Alice)


def test_load_csv_aliases_and_case_insensitive():
    base = whr.Base()
    # Using aliased headers like p1, p2, outcome, day, komi in mixed case
    csv_data = """P1,p2,OutCome,daY,KoMi
Alice,Carol,draw,0,0
Bob,Dave,black,10,0.0
Dave,Alice,white,30,10.0
"""
    f = io.StringIO(csv_data)
    
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        base.load_csv(f)

    assert len(base.ratings_for_player("Alice")) == 2
    assert len(base.ratings_for_player("Bob")) == 1


def test_load_csv_positional_fallback():
    base = whr.Base()
    # No header matching the aliases at all
    csv_data = """SomeHeader,AnotherHeader,ThirdHeader,FourthHeader,FifthHeader
Alice,Carol,D,0,0.0
Bob,Dave,B,10,0.0
"""
    f = io.StringIO(csv_data)
    
    # We expect multiple warnings because the header row is treated as data and contains invalid values
    with pytest.warns(UserWarning) as record:
        base.load_csv(f)

    messages = [w.message.args[0] for w in record]
    assert any("No CSV header detected. Falling back to default column order" in msg for msg in messages)
    assert any("Invalid winner 'ThirdHeader'" in msg for msg in messages)
    assert any("Invalid time_step 'FourthHeader'" in msg for msg in messages)
    assert any("Invalid handicap 'FifthHeader'" in msg for msg in messages)

    assert len(base.ratings_for_player("Alice")) == 1
    assert len(base.ratings_for_player("Bob")) == 1


def test_load_csv_empty_file():
    base = whr.Base()
    f = io.StringIO("")
    with pytest.warns(UserWarning, match="The CSV file is empty"):
        base.load_csv(f)


def test_load_csv_missing_or_malformed_values():
    base = whr.Base()
    csv_data = """black,white,winner,time_step,handicap
# Row 2: Missing black player (should skip and warn)
,Carol,D,0,0.0
# Row 3: Missing white player (should skip and warn)
Alice,,D,0,0.0
# Row 4: Self-play (should skip and warn)
Alice,Alice,W,5,0.0
# Row 5: Missing winner (default to D)
Alice,Carol,,0,0.0
# Row 6: Invalid winner (default to D)
Alice,Carol,invalid_result,0,0.0
# Row 7: Missing time_step (default to 0)
Alice,Carol,W,,0.0
# Row 8: Invalid time_step (warn and default to 0)
Alice,Carol,W,invalid_time,0.0
# Row 9: Float time_step (should round to int 12)
Alice,Carol,W,11.6,0.0
# Row 10: Invalid handicap (warn and default to 0.0)
Alice,Carol,W,10,invalid_handicap
"""
    f = io.StringIO(csv_data)
    
    # We expect multiple warnings
    with pytest.warns(UserWarning) as record:
        base.load_csv(f)

    # Let's verify warnings count or check their content
    warning_messages = [w.message.args[0] for w in record]
    assert any("Missing player name" in msg for msg in warning_messages)
    assert any("Self-play detected" in msg for msg in warning_messages)
    assert any("Missing winner" in msg for msg in warning_messages)
    assert any("Invalid winner" in msg for msg in warning_messages)
    assert any("Missing time_step" in msg for msg in warning_messages)
    assert any("Invalid time_step" in msg for msg in warning_messages)
    assert any("Invalid handicap" in msg for msg in warning_messages)

    # Check if the float time step rounded correctly to 12
    alice_games = base.ratings_for_player("Alice")
    # Float time step row is Row 9: Alice, Carol, W, 11.6, 0.0 -> time_step = 12
    days = [r[0] for r in alice_games]
    assert 12 in days
