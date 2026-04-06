import random
import time

from combat_loop import combat_loop
from utilities import tic, toc, load_spells

n = 10000

tic()
spells = load_spells("all_spells.json")
results = [combat_loop("characters.json", spells) for _ in range(n)]
toc()

print(f"Win percentage: {results.count("Heroes Win")/n*100}%")
