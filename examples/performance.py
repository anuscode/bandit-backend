import time

from mab import ThompsonBandit

bandits = [ThompsonBandit(item_id=str(x)) for x in range(1000000)]


s = time.time()

test = [_ for _ in bandits]

e = time.time()

print(e - s)
