from typing import Any


class Card:

    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        action: str,
    ) -> None: ...


def build_card(data: dict[str, Any]) -> Card: 
    return Card(data["id"], data["title"], data["description"], data["action"])

