from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from tile import Property


def should_buy_property(player:Player, prop:Property) -> bool:
    if player.strategy() == "Advanced":
        reserves = 200
        return (player.money() - prop.get_price()) > reserves
    else:
        return player.money() >= prop.get_price()

def should_build_house(player:Player, prop:Property) -> bool:
    if player.strategy() == "Advanced":
        return player.has_color_set(prop.color) and player.money() > 1000
    else:
        return False