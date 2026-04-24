import random
import time
import copy

from combat_loop import combat_loop
from utilities import tic, toc, load_spells, load_character_json

n = 10000

tic()
spells = load_spells("all_spells.json")
test_party = load_character_json("characters.json")
for ac_bonus in range(-14, 5):
    run_party = copy.deepcopy(test_party)
    run_party[0]['ac'] += ac_bonus
    results = [combat_loop(run_party, spells) for _ in range(n)]
    print(f"Win percentage: {results.count("Heroes Win")/n*100}% for AC {run_party[0]['ac']}")
toc()
