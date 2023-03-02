import collections
import math
import time
from typing import Optional, Iterable, Dict, Tuple, List, Union

import llist
import numpy as np
import scipy
from matplotlib import pyplot as plt

import annotations
from mab.abstracts import MAB
from mab.context import Context


Prediction = collections.namedtuple("Prediction", ["item_id", "score", "alpha", "beta"])

Observation = collections.namedtuple("Observation", ["item_id", "alpha", "beta"])


class ThompsonBandit(MAB):
    def __init__(
        self,
        item_id: str,
        created_at: Optional[float] = None,
        contexts: Iterable[Context] = tuple(),
        pool_size: int = 1000,
    ):
        super(ThompsonBandit, self).__init__()
        self._item_id = item_id
        self._created_at = created_at or time.time()
        self.pool_size = pool_size
        self.contexts = llist.dllist()
        self._alpha = 0
        self._beta = 0

        contexts = sorted(contexts, key=lambda x: x.updated_at)
        for context in contexts:
            self.update(context)

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def alpha(self) -> int:
        return self._alpha

    @property
    def beta(self) -> int:
        return self._beta

    @property
    def total(self) -> int:
        return self.alpha + self.beta

    @property
    def last_context(self) -> Optional[Context]:
        if self.contexts.last:
            return self.contexts.last.value
        return None

    @property
    def explore(self) -> float:
        if not self.last_context:
            return 0
        current_seconds = time.time()
        delta_seconds = current_seconds - self.last_context.updated_at
        delta_minutes = delta_seconds // 60
        if delta_minutes <= 0:
            return 0
        return min(float(delta_minutes / 5), 1)

    @property
    def exploit(self) -> float:
        return float(1 - self.explore)

    @annotations.elapsed
    def pull(self, explorable: bool = True) -> Prediction:
        """
        Slot machine 을 당겨서 reward 를 받는다.

        - alpha: reward 가 나온 횟수
        - beta: reward 가 나오지 않은 횟수
        - exploit: 정상적인 reward 를 반영 할 백분위.
        - explore: 1 - exploit, 이 값은 regret 값과 곱해져서 탐험에 기여하는 값이 된다.
        - reward: 1 or 0
        - regret: log scale 을 씌워 더 넓은 확률 분포를 가지도록 만든 임의의 값 기댓값이 너무 빨리 수렴되어 정확한 reward 에 도달되지 못하는 것을 막기 위해 탐험의 확률을 높이는 일을 한다.

        :return: expected reward score as float between 0 to 1.
        """
        alpha, beta = self._alpha + 1, self._beta + 1
        regret_a, regret_b = math.log(alpha, math.e), math.log(beta, math.e)
        reward = np.random.beta(alpha, beta)

        if not explorable:
            prediction = Prediction(
                item_id=self.item_id, score=reward, alpha=alpha, beta=beta
            )
            return prediction

        regret = np.random.beta(regret_a + 1, regret_b + 1)
        explore = self.explore
        exploit = 1 - explore
        score = (reward * exploit) + (regret * explore)
        prediction = Prediction(item_id=self.item_id, score=score, alpha=alpha, beta=beta)
        return prediction

    def mean(self) -> float:
        return self._alpha / self.total

    def observation(self) -> Observation:
        return Observation(item_id=self.item_id, alpha=self.alpha, beta=self.beta)

    def update(self, c: Context):

        if c.value == -1:
            return

        if c.value == 1:
            nodes = list(self.contexts.iternodes())
            for node in reversed(nodes):
                if node.value.value == 0:
                    self.contexts.remove(node)
                    self._beta -= 1
                    break

            self._alpha += 1
        elif c.value == 0:
            self._beta += 1
        else:
            raise ValueError(f"Invalid context value: {c.value}")

        self.contexts.append(c)

        if len(self.contexts) > self.pool_size:
            context = self.contexts.popleft()
            if context.value == 1:
                self._alpha -= 1
            else:
                self._beta -= 1

    def reset(self):
        self._alpha = 0
        self._beta = 0
        self.contexts = llist.dllist()

    def draw_beta_distribution(self):
        x = np.linspace(0.01, 0.99, 99)
        y = scipy.stats.beta(self._alpha, self._beta).pdf(x)
        plt.figure(figsize=(12, 8))
        plt.plot(x, y, "r")
        plt.xlabel("X")
        plt.ylabel("P(X)")
        plt.grid()
        plt.title("Beta Distribution")
        plt.show()

    def __str__(self):
        return (
            f"ThompsonBandit("
            f"item_id='{self.item_id}', "
            f"alpha={self._alpha}, "
            f"beta={self._beta}"
            f")"
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        results = [
            self.item_id == other.item_id,
            self.alpha == other.alpha,
            self.beta == other.beta,
        ]
        return all(results)


class ThompsonMultiArmedBandit(MAB):
    def __init__(self, bandits: Iterable[ThompsonBandit] = tuple()):
        self._bandits = {x.item_id: x for x in bandits}

    @property
    def bandits(self) -> Dict[str, ThompsonBandit]:
        return self._bandits

    @annotations.elapsed
    def pull(self, explorable: bool = True) -> List[Prediction]:
        """
        Slot machine 을 당겨서 rewards 를 받는다.

        - alpha: reward 가 나온 횟수.
        - beta: reward 가 나오지 않은 횟수.
        - exploit: 정상적인 reward 를 반영 할 백분위.
        - explore: 1 - exploit, 이 값은 regret 값과 곱해져서 탐험에 기여하는 값이 된다.
        - reward: 1 or 0.
        - regret: log scale 을 씌워 더 넓은 확률 분포를 가지도록 만든 임의의 값 기댓값이 너무 빨리 수렴되어 정확한 reward 에 도달되지 못하는 것을 막기 위해 탐험의 확률을 높이는 일을 한다.

        :return: a tuple list consists of (id, reward)
        """

        bandits = [x for x in self.bandits.values()]

        if not bandits:
            return []

        bandits_matrix = [(x.alpha + 1, x.beta + 1, x.explore) for x in bandits]
        bandits_matrix = np.array(bandits_matrix)

        alphas, betas = bandits_matrix[:, 0], bandits_matrix[:, 1]
        regret_a, regret_b = np.log(alphas) + 1, np.log(betas) + 1

        rewards = np.random.beta(alphas, betas)

        if not explorable:
            ranked_indices = np.argsort(rewards)[::-1]
            ranked_bandits = tuple(bandits[x] for x in ranked_indices)
            ranked_rewards = tuple(rewards[x] for x in ranked_indices)
            return [
                (x.item_id, y, x.alpha, x.beta)
                for x, y in zip(ranked_bandits, ranked_rewards)
            ]

        regrets = np.random.beta(regret_a, regret_b)
        explores = bandits_matrix[:, 2]
        exploits = 1 - explores
        rewards = (rewards * exploits) + (regrets * explores)

        ranked_indices = np.argsort(rewards)[::-1]
        ranked_bandits = tuple(bandits[x] for x in ranked_indices)
        ranked_rewards = tuple(rewards[x] for x in ranked_indices)

        result = [
            Prediction(item_id=x.item_id, score=y, alpha=x.alpha, beta=x.beta)
            for x, y in zip(ranked_bandits, ranked_rewards)
        ]
        return result

    def means(self) -> List[Tuple[str, float]]:
        return [(x.item_id, x.mean()) for x in self.bandits.values()]

    def observations(self) -> List[Observation]:
        return [x.observation() for x in self.bandits.values()]

    def update(self, c: Context):
        bandit = self.bandits.get(c.item_id, None)
        if not bandit:
            bandit = ThompsonBandit(item_id=c.item_id, created_at=c.updated_at)
            self._bandits[c.item_id] = bandit
        bandit.update(c)

    def delete(self, key_or_keys: Union[str, Iterable[str]]) -> List[ThompsonBandit]:
        if isinstance(key_or_keys, str):
            deleted = self._bandits.pop(key_or_keys, None)
            return [deleted]

        if isinstance(key_or_keys, Iterable):
            getter = self._bandits.get
            deleted = [getter(k, None) for k in key_or_keys]
            self._bandits = {
                k: v for k, v in self._bandits.items() if k not in key_or_keys
            }
            return deleted

    def reset(self):
        for bandit in self.bandits.values():
            bandit.reset()

    def draw_beta_distribution(self, item_id: str):
        bandit = self.bandits.get(item_id, None)
        if bandit:
            bandit.draw_beta_distribution()

    def __str__(self):
        return f"ThompsonMultiArmedBandit: {len(self.bandits)} bandits"
