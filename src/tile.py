from __future__ import annotations
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from board import Board
    from player import Player


class Tile:
    """Base class for all board tiles."""

    def __init__(
        self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        description: str,
    ): 
        self._board = board
        self._position = position
        self._name = name
        self._tile_type = tile_type
        self._description = description

    def land_on(self, player: Player) -> None:
        """Handle what happens when a player lands on this tile."""
        print(f"You've landed on {self._name}")
        if self._tile_type == "property":
            ...
        elif self._tile_type == "station":
            ...
        elif self._tile_type == "tax":
            ...
        elif self._tile_type == "utility":
            ...
        elif self._tile_type == "community_chest" or self._tile_type == "chance":
            ...
        else:
            ...

    def type(self) -> str: return self._tile_type
    def name(self) -> str: return self._name
    def description(self) -> str: return self._description
    def position(self) -> int: return self._position
    def board(self) -> Board: return self._board


class Property(Tile):
    '''Class for all individual properties'''
    def __init__(
        self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        color:str,
        price: int,
        rent: int,
        mortgage: int,
    ): 
        super().__init__(board,position,name,tile_type,'')
        self._price = price
        self._rent = rent
        self._mortgage = mortgage
        self.color = color


class Street(Property):
    '''Subclass from the property class for streets'''
    def __init__(
        self,
        board: Board,
        position: int,
        name: str,
        tile_type: str,
        color: str,
        price: int,
        rent: int,
        rent_with_color_set: int,
        rent_with_1_house: int,
        rent_with_2_houses: int,
        rent_with_3_houses: int,
        rent_with_4_houses: int,
        rent_with_hotel: int,
        house_cost: int,
        hotel_cost: int,
        mortgage: int,
    ): 
        super().__init__(board,position,name,tile_type,color,price,rent,mortgage)
        self._rent_with_color_set = rent_with_color_set
        self._rent_with_1_house = rent_with_1_house
        self._rent_with_2_houses = rent_with_2_houses
        self._rent_with_3_houses = rent_with_3_houses
        self._rent_with_4_houses = rent_with_4_houses
        self._rent_with_hotel = rent_with_hotel
        self._house_cost = house_cost
        self._hotelcost = hotel_cost


class Station(Tile):
    '''Subclass from the class tile for train stations'''
    def __init__(
        self, 
        board: Board, 
        position: int, 
        name: str, 
        tile_type: str, 
        price: str,
        rent: int,
        rentWith2Stations: int,
        rentWith3Stations: int,
        rentWith4Stations: int,
    ):
        super().__init__(board, position, name, tile_type, '')
        self._price = price
        self._rent = rent
        self._rentWith2Stations = rentWith2Stations
        self._rentWith3Stations = rentWith3Stations
        self._rentWith4Stations = rentWith4Stations


class Utility(Tile):
    '''Subclass from the class tile for utility tiles'''
    def __init__(
        self, 
        board: Board,
        position: int, 
        name: str, 
        tile_type: str, 
        price:int, 
        rentMultiplier:int, 
        rentMultiplierWithBoth:int, 
        description: str, 
        mortgage:int
        ):
        super().__init__(board, position, name, tile_type, description)
        self._price = price
        self._rentMultiplier = rentMultiplier
        self._rentMultiplierWithBoth = rentMultiplierWithBoth
        self._mortgage = mortgage


class Tax(Tile):
    '''Subclass from the tile class for tax tiles'''
    def __init__(self, board: Board, position: int, name: str, tile_type: str, amount:int, description: str):
        super().__init__(board, position, name, tile_type, description)
        self._amount = amount



def build_tile(board: Board, data: dict[str, Any]) -> Tile:
    tile_type = data["type"]

    if tile_type == 'property':
        return Property(board, data['position'], data['name'], data['type'], data["color"], data["price"], data["rent"], data["mortgage"])
    elif tile_type == 'tax':
        return Tax(board, data['position'], data['name'], data['type'], data["amount"], data['description'])
    elif tile_type == 'station':
        return Station(board, data['position'], data['name'], data['type'], data["price"], data["rent"], data["rentWith2Stations"], data["rentWith3Stations"], data["rentWith4Stations"])
    elif tile_type == 'utility':
        return Utility(board, data['position'], data['name'], data['type'], data["price"], data["rentMultiplier"], data["rentMultiplierWithBoth"], data["description"], data['mortgage'])
    else:     
        return Tile(board, data['position'], data['name'], data['type'], data['description'])

    

