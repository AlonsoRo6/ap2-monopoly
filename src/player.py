from __future__ import annotations
from typing import TYPE_CHECKING, Any
import const
from strategy import *

if TYPE_CHECKING:
    from board import Board
    from tile import Property, Tile



class Player:
    _board: Board
    _name: str
    _piece: str
    _color: str
    _index: int
    _position: int
    _money: int

    def __init__(
        self,
        board: Board,
        name: str,
        piece: str,
        color: str,
        index: int,
    ): 
        self._board = board
        self._name = name
        self._piece = piece
        self._color = color
        self._index = index
        self._position = 0
        self._money = const.START_MONEY
        self._owned_properties:list[Property] = []
        self._get_out_of_jail_free_cards = 0
        self._in_prison = False
        self._turns_in_prison = 0
        self._bankruptcy = False


        if self._index % 2 == 0:
            self._strategy = "Advanced"
        else:
            self._strategy = "Simple"


    def board(self) -> Board: return self._board

    def name(self) -> str: 
        '''Returns the player's name'''
        return self._name

    def piece(self) -> str: 
        '''Returns the player's piece'''
        return self._piece

    def color(self) -> str: 
        '''Returns the player's color'''
        return self._color

    def index(self) -> int: 
        '''Returns the player's index'''
        return self._index

    def broke(self) -> bool:
        """Return True if the player has negative money."""
        return self._money < 0

    def money(self) -> int: 
        '''Returns the player's money'''
        return self._money

    def position(self) -> int: 
        '''Returns the player's position'''
        return self._position

    def is_bankrupt(self) -> bool:
        '''Returns true if the player is bankrupt'''
        return self._bankruptcy

    def get_out_of_jail_free_cards(self) -> int: 
        '''Returns the amount of get out of jail card the player has'''
        return self._get_out_of_jail_free_cards

    def turns_in_prison(self) -> int: 
        '''Returns the amount of turns the player has spent in prison'''
        return self._turns_in_prison

    def owned_properties(self) -> list[Property]: 
        '''Returns a list of Property with all properties owned by the player'''
        return self._owned_properties

    def has_color_set(self, color:str) -> bool:
        '''Returns True if the player has the color set of the color given'''
        amount = sum(1 for property in self.owned_properties() if getattr(property,"color",None) == color)
        
        total_of_color = sum(1 for t in self.board().tiles() if getattr(t, "color", None) == color)

        return amount == total_of_color

    def amount_stations(self) -> int:
        '''Returns the amount of stations the player has'''
        amount = sum(1 for property in self.owned_properties() if property.type() == "station")
        return amount

    def has_all_utilities(self) -> bool:
        '''Returns True if the player has both utilities'''
        amount = sum(1 for property in self.owned_properties() if property.type() == "utility")
        return amount == 2
    
    def add_money(self, amount:int) -> None: 
        '''Method that adds the given amount to the player's money'''
        self._money += amount

    def new_property(self, property: Property) -> None:
        '''Method that adds the given property to the player's list of owned properties'''
        self._owned_properties.append(property)
  
    def move(self, steps:int, board:Board) -> None:
        '''Experimntal method to move a player across the board'''
        old_position = self._position
        self._position = (old_position + steps) % 40

        print(f'La nova posició és {self._position}')

    def move_to(self,go_position:int) -> None:
        '''Method that moves a player to a given position'''
        self._position = go_position

    def strategy(self) -> str:
        '''Returns a string with the name of the player's strategy'''
        return self._strategy


    def post_turn_actions(self) -> None:
        '''Method that executes the post-turn actions if necessary'''
        for property in self.owned_properties():
            from tile import Street
            if isinstance(property,Street) and should_build_house(self,property): #build house
                self.add_money(-property.get_house_cost())
                property.buy_house()
                
            if isinstance(property,Street): #sell house
                while should_sell_house(self,property):
                    self.add_money(property.get_house_cost())
                    property.sell_house()
            
            if should_mortgage_property(self, property): #mortgage
                self.add_money(property.get_mortgage())
                property.mortgage()
            
            if property.is_tile_mortgaged() and should_unmortgage_property(self,property): #unmortgage
                self.add_money(-property.get_unmortgage_price())
                property.unmortgage()


    def find_next_tile_of_type(self, board:Board, tile_type: str) -> Tile:
        '''Returns the nearest tile of the same type as the given tyle_type'''
        tiles = board.tiles()
        num_tiles = len(tiles)
        for i in range(1, num_tiles + 1):
            next_index = (self.position() + i) % num_tiles
            tile = tiles[next_index]
            if tile.type() == tile_type:
                return tile
        
        return tiles[0]
    

    #funcions gestió pressó
    def add_get_out_of_jail_card(self) -> None:
        '''Method that adds one get out of jail card to this player'''
        self._get_out_of_jail_free_cards += 1

    def use_get_out_of_jail_card(self) -> None:
        '''Method that uses one of the get oout of jail cards of this player'''
        self._get_out_of_jail_free_cards -= 1

    def put_in_prison(self) -> None:
        '''Method that "internally" puts in prison this player'''
        self._in_prison = True

    def release_from_prison(self) -> None:
        '''Method that "internally" releases from prison this player'''
        self._in_prison = False
        self._turns_in_prison = 0

    def is_in_prison(self) -> bool:
        '''Method that return true if the player is in prison'''
        return self._in_prison

    def add_turn_in_prison(self) -> None:
        '''Method that adds one to the amount of turns the player has spent in prison'''
        self._turns_in_prison += 1


    def clear_properties(self) -> None:
        '''When a player goes bankrupt to the bank, all of its properties go to the bank'''
        for property in self.owned_properties():
            from tile import Street
            if isinstance(property,Street):
                while property.amount_houses() > 0:
                    property.sell_house()
            if property.is_tile_mortgaged():
                property.unmortgage()
            property.set_owner(None)

    def transfer_properties(self,transfer_player:Player,board:Board) -> None:
        '''When a player goes bankrupt to another player, all of its properties go to the other player'''

        for _ in range(self.get_out_of_jail_free_cards()): #traspassem les cartes per sortir de la presó
            transfer_player.add_get_out_of_jail_card()

        for property in self.owned_properties():
            property.set_owner(transfer_player)
            transfer_player.new_property(property)
            
            if property.is_tile_mortgaged():
                unmortgage_price = property.get_unmortgage_price()
                ten_percent_mortgage = int(property.get_mortgage() * 0.1)

                if transfer_player.money() > unmortgage_price: #unmortgage
                    transfer_player.add_money(-unmortgage_price)
                    property.unmortgage()
                elif transfer_player.money() > ten_percent_mortgage: #keep mortgaged
                    transfer_player.add_money(-ten_percent_mortgage)
                else:
                    transfer_player.bankruptcy(None,board) #si no pot pagar res d'això, en bancarrota
                    return
        
        
    def bankruptcy(self, transfer_player:Player|None,board:Board) -> None:
        '''Method that handles what happens when a player goes bankrupt, either to another player or to the bank'''
        if transfer_player == None:
            self.clear_properties()
        else:
            transfer_player.add_money(self.money())
            self.transfer_properties(transfer_player,board)

        self._money = 0
        self.owned_properties().clear()
        self._get_out_of_jail_free_cards = 0
        board.eliminate_player()
        self._bankruptcy = True
    

def build_player(board: Board, data: dict[str, Any]) -> Player:
    """Build a Player from JSON-like dict with 'name', 'piece', and 'color' keys."""
    return Player(board, data["name"], data["piece"], data["color"], data["index"])
