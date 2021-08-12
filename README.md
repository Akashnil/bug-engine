# bug-engine
[Bug](https://boardgamegeek.com/boardgame/240835/bug) is a 2 player combinatorial game where shapes are built on a hexagonal board. The standard board size (3 X 3 X 3) is possible to search using brute force. There are 51148504 different positions modulo rotations and reflections of the hexagonal board. The game value of each position can be stored in memory in a hash map.

The python file in bug-engine.py can search the entire space and save game values in a dictionary. After ~3 hours of calculation, it writes the dictionary in a pickle file, which can be read later in a few seconds. Once the dictionary is loaded into memory, evaluating positions and finding best moves are instantaneous.

Example games are included in txt files (engine vs engine and engine vs random player).
