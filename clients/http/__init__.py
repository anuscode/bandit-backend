import random
from typing import Dict, Any, NoReturn, List

import requests


def stack_debug_distribution(
    user_id: str,
    distribution_id: str,
    arguments: List[Dict[str, Any]],
) -> NoReturn:
    try:
        url = f"http://a2496f7abc0504ac4a081b6208df2141-2138106660.ap-northeast-2.elb.amazonaws.com/v1/debugs/{user_id}/distributions/{distribution_id}"
        response = requests.post(url, json=arguments)
        response.raise_for_status()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    stack_debug_distribution(
        "test",
        "test",
        [{"article_id": f"test_{x}", "score": random.uniform(0, 1)} for x in range(2)],
    )
