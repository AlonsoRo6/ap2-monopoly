from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from tile import Property, Street


def should_buy_property(player:Player, prop:Property) -> bool:
    if player.strategy() == "Advanced":
        reserves = 200
        return (player.money() - prop.get_price()) > reserves
    else:
        return player.money() >= prop.get_price()

def should_build_house(player:Player, prop:Street) -> bool:
    if player.strategy() == "Advanced":
        return prop.can_build_house() and player.money() > 400
    else:
        return False
    
def should_sell_house(player:Player,prop:Street) -> bool:
    if player.strategy() == "Advanced":
        return prop.can_sell_house() and player.money() < 200
    else:
        return False
    
def should_mortgage_property(player:Player, prop:Property) -> bool:
    if player.strategy() == "Advanced":
        return prop.can_mortgage() and player.money() < 200
    else:
        return False
    
def should_demortgage_property(player:Player, prop:Property) -> bool:
    if player.strategy() == "Advanced":
        return player.money() > 1000
    else:
        return False

