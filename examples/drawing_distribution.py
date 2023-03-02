import random
import time

from mab import Context, ThompsonBandit


def value():
    return random.choice([0, 0, 0, 1])


bandit = ThompsonBandit(contexts=[], item_id="1")


for _ in range(1000):
    c = Context(
        item_id="1",
        value=value(),
        updated_at=time.time(),
    )
    bandit.update(c)

    if _ % 10 == 0:
        bandit.draw_beta_distribution()
        time.sleep(0.1)


def value2():
    return random.choice([0, 1, 1, 1])


for _ in range(150):
    c = Context(
        item_id="1",
        value=value2(),
        updated_at=time.time(),
    )
    bandit.update(c)

    if _ % 10 == 0:
        bandit.draw_beta_distribution()
        time.sleep(0.1)
