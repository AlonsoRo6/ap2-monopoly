from __future__ import annotations
from typing import TYPE_CHECKING, Any

from strategy import *


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

    def land_on(self, player: Player, rent_multiplier:int, board:Board) -> None:
        """Handle what happens when a player lands on this tile."""
        if self._tile_type == "property":            
            print(f"You've landed on a property")
        elif self._tile_type == "station":
            print(f"You've landed on a station")
        elif self._tile_type == "tax":
            print(f"You've landed on tax")
        elif self._tile_type == "utility":
            print(f"You've landed on a utility")
        elif self._tile_type == "community_chest" or self._tile_type == "chance":
            print(f"You've landed on a card")
        elif self._tile_type == "special" and self._description == "Go directly to jail":
            player.move_to(10)
            player.put_in_prison()
        else:
            print(f"You've landed else")

    def type(self) -> str:
        '''Returns the tile's type'''
        return self._tile_type
    def name(self) -> str: 
        '''Returns the tile's name'''
        return self._name
    def description(self) -> str: 
        '''Returns the tile's description'''
        return self._description
    def position(self) -> int: 
        '''Returns the tile's position'''
        return self._position
    def board(self) -> Board: 
        '''Returns the board'''
        return self._board


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
        self.price = price
        self._rent = rent
        self._mortgage = mortgage
        self.color = color
        self.owner: Player | None = None
        self.is_mortgaged = False

    def get_owner(self) -> Player | None:
        '''Returns the property owner'''
        return self.owner
    
    def set_owner(self, player:Player|None) -> None:
        '''Method that sets the given player as the owner of this Property'''
        self.owner = player

    def is_tile_mortgaged(self) -> bool:
        '''Returns true if the property's mortgaged'''
        return self.is_mortgaged
    
    def get_price(self) -> int:
        '''Returns the property price'''
        return self.price
    
    def get_rent(self) -> int:
        '''Returns the property rent'''
        return self._rent
    
    def get_mortgage(self) -> int:
        return self._mortgage
    
    def can_mortgage(self) -> bool:
        '''Returns true if the property can be mortgaged'''
        if self.is_tile_mortgaged():
            return False
        owner = self.get_owner()
        assert owner is not None
        if any([street.amount_houses() > 0 for street in owner.owned_properties() if isinstance(street,Street) and street.color == self.color]):
            return False
        return True

    def get_unmortgage_price(self) -> int:
        '''Returns the price that has to be paid for the property to be unmortgaged'''
        return int(self.get_mortgage() + self.get_mortgage() * 0.1)

    def mortgage(self) -> None:
        '''Method that "internally" sets the property to mortgaged'''
        self.is_mortgaged = True
    
    def unmortgage(self) -> None:
        '''Method that "internally" sets the property to unmortgaged'''
        self.is_mortgaged = False


    def land_on(self, player: Player, rent_multiplier:int, board:Board) -> None:
        '''Handles what happens when a player lands on a property'''
        owner = self.get_owner()
        if owner == None:
            if should_buy_property(player,self):
                player.add_money(-self.get_price())
                player.new_property(self)
                self.set_owner(player)
        elif owner != player:
            if not self.is_tile_mortgaged():
                rent = self.get_rent()
                owner.add_money(rent*rent_multiplier)
                player.add_money(-rent*rent_multiplier)


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
        
        self.houses = 0  
        self.hotels = 0 

    def get_rent(self) -> int: 
        '''Returns the street rent, taking into account all variables'''
        owner = self.get_owner()
        assert owner != None
        if owner.has_color_set(self.color):
            if self.amount_houses() == 0:
                return self._rent_with_color_set
            if self.amount_houses() == 1:
                return self._rent_with_1_house
            elif self.amount_houses() == 2:
                return self._rent_with_2_houses
            elif self.amount_houses() == 3:
                return self._rent_with_3_houses
            elif self.amount_houses() == 4:
                return self._rent_with_4_houses
            else:
                return self._rent_with_hotel
        else:
            return self._rent
    
    def get_house_cost(self) -> int:
        '''Method that returns the price of the next house or hotel for this Street'''
        if self.amount_houses() == 4:
            return self._hotelcost
        else:
            return self._house_cost

    def buy_house(self) -> None:
        '''Adds a house to the street'''
        self.houses += 1
        if self.houses == 5:
            self.hotels = 1

    def sell_house(self) -> None:
        '''Sells a house of this street'''
        self.houses -= 1
        if self.hotels == 1:
            self.hotels -= 1

    def amount_houses(self) -> int:
        '''Returns the amount of houses (5 if hotel) the street has'''
        return self.houses
    
    def can_build_house(self) -> bool:
        '''Returns true if the player can build a house or hotel on this street'''
        owner = self.get_owner()
        assert owner is not None
        houses = self.amount_houses()
        
        if houses > 5 or not owner.has_color_set(self.color) or owner.money() < self.get_house_cost(): 
            return False
        
        if not owner.has_color_set(self.color):
            return False 
        
        color_set = [street for street in owner.owned_properties()if isinstance(street,Street) and street.color == self.color and street != self]
        
        if any([street.is_tile_mortgaged() for street in color_set]):
            return False
        
        houses_same_color = [street.amount_houses() for street in color_set]
        
        if houses <= max(houses_same_color):
            return True
        
        return False
    
    def can_sell_house(self) -> bool:
        '''Returns true if the player can sell a house or hotel on this street'''
        owner = self.get_owner()
        assert owner is not None
        houses = self.amount_houses()

        if houses > 1:
            return False

        color_set = [street for street in owner.owned_properties()if isinstance(street,Street) and street.color == self.color and street != self]
        houses_same_color = [street.amount_houses() for street in color_set]

        if houses >= max(houses_same_color):
            return True
        
        return False
    

class Station(Property):
    '''Subclass from the class Property for train stations'''
    def __init__(
        self, 
        board: Board, 
        position: int, 
        name: str, 
        tile_type: str, 
        price: int,
        rent: int,
        rentWith2Stations: int,
        rentWith3Stations: int,
        rentWith4Stations: int,
        mortgage: int
    ):
        super().__init__(board, position, name, tile_type, '', price, rent, mortgage)
        self._rentWith2Stations = rentWith2Stations
        self._rentWith3Stations = rentWith3Stations
        self._rentWith4Stations = rentWith4Stations

        
    def get_rent(self) -> int: 
        '''Returns the station rent, taking into account all variables'''
        owner = self.get_owner()
        assert owner != None
        if owner.amount_stations() == 1:
            return self._rent
        elif owner.amount_stations() == 2:
            return self._rentWith2Stations
        elif owner.amount_stations() == 3:
            return self._rentWith3Stations
        else: 
            return self._rentWith4Stations
        
class Utility(Property):
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
        super().__init__(board, position, name, tile_type, '', price, 0, mortgage)
        
        self._rentMultiplier = rentMultiplier
        self._rentMultiplierWithBoth = rentMultiplierWithBoth
        self._description = description

    def get_rent(self) -> int:
        '''Returns the utility rent, taking into account all variables'''
        owner = self.get_owner()
        assert owner != None
        if owner.has_all_utilities():
            return sum(self._board.dice()) * 10
        else: 
            return sum(self._board.dice()) * 4


class Tax(Tile):
    '''Subclass from the Property class for tax tiles'''
    def __init__(self, board: Board, position: int, name: str, tile_type: str, amount:int, description: str):
        super().__init__(board, position, name, tile_type, description)
        self._amount = amount

    def land_on(self,player:Player,rent_multiplier:int,board:Board) -> None:
        player.add_money(-self._amount)


class Card(Tile):
    def __init__(self, board: Board, position: int, name: str, tile_type: str, description: str):
        super().__init__(board, position, name, tile_type, description)
    
    def get_type(self) -> str:
        return self._tile_type
    
    def land_on(self, player: Player, rent_multiplier: int, board:Board) -> None:
        card = board.get_deck(self.get_type()).get_card()
        card.execute(player,board)
        print(card.action())


def build_tile(board: Board, data: dict[str, Any]) -> Tile:
    '''Build the tile, with a different subclass depending on its type'''
    tile_type = data["type"]

    if tile_type == 'property':
        return Street(board, data['position'], data['name'], data['type'], data["color"], data["price"], data["rent"], data["rentWithColorSet"], data["rentWith1House"], data["rentWith2Houses"], data["rentWith3Houses"], data["rentWith4Houses"], data["rentWithHotel"], data["houseCost"], data["hotelCost"], data["mortgage"])
    elif tile_type == 'tax':
        return Tax(board, data['position'], data['name'], data['type'], data["amount"], data['description'])
    elif tile_type == 'station':
        return Station(board, data['position'], data['name'], data['type'], data["price"], data["rent"], data["rentWith2Stations"], data["rentWith3Stations"], data["rentWith4Stations"], data["mortgage"])
    elif tile_type == 'utility':
        return Utility(board, data['position'], data['name'], data['type'], data["price"], data["rentMultiplier"], data["rentMultiplierWithBoth"], data["description"], data['mortgage'])
    elif tile_type == 'chance' or tile_type == 'community_chest':
        return Card(board, data['position'], data['name'], data['type'], data['description'])
    else:     
        return Tile(board, data['position'], data['name'], data['type'], data['description'])

    

