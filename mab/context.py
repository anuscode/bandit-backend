import collections
from dataclasses import dataclass, field

Context = collections.namedtuple("Context", ["item_id", "value", "updated_at"])


# @dataclass
# class Context:
#     item_id: str
#     author_id: str | None = None
#     value: str = field(default='Bravo')
#     updated_at: str = field(default='Charlie')
