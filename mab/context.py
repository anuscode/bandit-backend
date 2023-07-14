from dataclasses import dataclass


@dataclass
class Context:
    item_id: str
    value: int
    updated_at: float
    author_id: str | None = None
