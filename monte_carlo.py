import random
import time

from combat_loop import combat_loop
from utilities import tic, toc

n = 10000

tic()
results = [combat_loop("characters.json") for _ in range(n)]
toc()

print(f"Win percentage: {results.count("Heroes Win")/n*100}%")
