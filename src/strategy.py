from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from tile import Property, Street


class Strategy:
    """Base class for player strategies. Subclasses define buying and building behaviour."""

    def should_buy_property(self, player: Player, prop: Property) -> bool:
        """Returns True if the player can and should buy the given property."""
        raise NotImplementedError
    def should_build_house(self, player: Player, prop: Street) -> bool:
        """Returns True if the player can and should build a house on the given street."""
        raise NotImplementedError
    def should_sell_house(self, player: Player, prop: Street) -> bool:
        """Returns True if the player can and should sell a house on the given street."""
        raise NotImplementedError
    def should_mortgage_property(self, player: Player, prop: Property) -> bool:
        """Returns True if the player can and should mortgage the given property."""
        raise NotImplementedError
    def should_unmortgage_property(self, player: Player, prop: Property) -> bool:
        """Returns True if the player can and should unmortgage the given property."""
        raise NotImplementedError


class SimpleStrategy(Strategy):
    """Simple strategy: always buy properties when affordable, never build or mortgage."""

    def should_buy_property(self, player: Player, prop: Property) -> bool:
        return player.money() >= prop.get_price()

    def should_build_house(self, player: Player, prop: Street) -> bool:
        return False
    def should_sell_house(self, player: Player, prop: Street) -> bool:
        return False
    def should_mortgage_property(self, player: Player, prop: Property) -> bool:
        return False
    def should_unmortgage_property(self, player: Player, prop: Property) -> bool:
        return False


class AdvancedStrategy(Strategy):
    """Advanced strategy: buy with reserves, build houses, sell/mortgage when low on cash."""

    _RESERVA_COMPRA = 200
    _RESERVA_CONSTRUIR = 150
    _MARGE_VENDA = 5
    _MARGE_HIPOTECA = 10
    _MARGE_DESHIPOTECA = 1000

    def should_buy_property(self, player: Player, prop: Property) -> bool:
        return (player.money() - prop.get_price()) > self._RESERVA_COMPRA

    def should_build_house(self, player: Player, prop: Street) -> bool:
        return (prop.can_build_house() and (player.money() - prop.get_house_cost()) > self._RESERVA_CONSTRUIR)

    def should_sell_house(self, player: Player, prop: Street) -> bool:
        return prop.can_sell_house() and player.money() < self._MARGE_VENDA

    def should_mortgage_property(self, player: Player, prop: Property) -> bool:
        return prop.can_mortgage() and player.money() < self._MARGE_HIPOTECA

    def should_unmortgage_property(self, player: Player, prop: Property) -> bool:
        return player.money() > self._MARGE_DESHIPOTECA
