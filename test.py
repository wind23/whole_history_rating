import whr

base = whr.Base()
base.create_game("shusaku", "shusai", "W", 1, 0)
base.create_game("shusaku", "shusai", "W", 1, 0)	
base.create_game("shusaku", "shusai", "B", 1, 0)
base.create_game("shusaku", "shusai", "B", 1, 0)
base.create_game("shusaku", "shusai", "W", 1, 0)
base.iterate(50)
print (base.ratings_for_player("shusaku"))
print (base.ratings_for_player("shusai"))
