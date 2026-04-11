import random
import time

from combat_loop import combat_loop
from utilities import tic, toc, load_spells, load_character_json

tic()
spells = load_spells("all_spells.json")
test_party = load_character_json("characters.json")
results = combat_loop(test_party, spells)
toc()

print(results)
