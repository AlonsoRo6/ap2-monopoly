from typing import Any


class Card:

    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        action: str,
    ) -> None: 
        self._id = id
        self._title = title
        self._description = description
        self._action = action


def build_card(data: dict[str, Any]) -> Card: 
    return Card(data["id"], data["title"], data["description"], data["action"])

