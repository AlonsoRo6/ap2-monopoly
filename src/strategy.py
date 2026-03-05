from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from tile import Property, Street


def should_buy_property(player:Player, prop:Property) -> bool:
    '''Return true if the player CAN and SHOULD buy the given property'''
    if player.strategy() == "Advanced":
        reserves = 200
        return (player.money() - prop.get_price()) > reserves
    else:
        return player.money() >= prop.get_price()

def should_build_house(player:Player, prop:Street) -> bool:
    '''Returns true if the player CAN and SHOULD build a house on the given property'''
    return player.strategy() == "Advanced" and prop.can_build_house()
    
    '''if player.strategy() == "Advanced":
        return prop.can_build_house() and player.money() > 400
    else:
        return False'''
    
def should_sell_house(player:Player,prop:Street) -> bool:
    '''Returns true if the player CAN and SHOULD sell a house of the given property'''
    if player.strategy() == "Advanced":
        return prop.can_sell_house() and player.money() < 5
    else:
        return False
    
def should_mortgage_property(player:Player, prop:Property) -> bool:
    '''Returns true if the player CAN and SHOULD mortgage the given property'''
    if player.strategy() == "Advanced":
        return prop.can_mortgage() and player.money() < 10
    else:
        return False
    
def should_unmortgage_property(player:Player, prop:Property) -> bool:
    '''Returns true if the player CAN and SHOULD unmortgage a property'''
    if player.strategy() == "Advanced":
        return player.money() > 1000
    else:
        return False

