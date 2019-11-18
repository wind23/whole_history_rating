import whr

whr = whr.Base()
whr.create_game("shusaku", "shusai", "W", 1, 0)
whr.create_game("shusaku", "shusai", "W", 1, 0)	
whr.create_game("shusaku", "shusai", "B", 1, 0)
whr.create_game("shusaku", "shusai", "B", 1, 0)
whr.create_game("shusaku", "shusai", "W", 1, 0)
whr.iterate(50)
print (whr.ratings_for_player("shusaku"))
print (whr.ratings_for_player("shusai"))
