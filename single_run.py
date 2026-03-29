import random
import time

from combat_loop import combat_loop
from utilities import tic, toc

n = 10000

tic()
results = combat_loop()
toc()

print(results)
