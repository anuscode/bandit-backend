import random
import time

from mab import ThompsonMultiArmedBandit, Context

mab = ThompsonMultiArmedBandit()

for i in range(100000):
    for _ in range(400):
        c = Context(
            item_id=f"item_id_{i}",
            value=random.choice([0, 1]),
        )

        mab.update(c)

s = time.time()
print(mab.pull())
e = time.time()
print(e - s)
