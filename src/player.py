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

    def get_out_of_jail_free_cards(self) -> int: return self._get_out_of_jail_free_cards

    def turns_in_prison(self) -> int: return 0

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

        if self._position < old_position: #falta afegir que no hagi anat a la presó
            self.add_money(const.GO_SALARY)
            print(f"You've gone through the GO tile and earned {const.GO_SALARY}$")
            print(self._money)
        
        current_tile = self._board.get_tile_index(self._position)
        current_tile.land_on(self,1,board)

        print(f'La nova posició és {self._position}')

    def move_to(self,go_position:int) -> None:
        '''Method that moves a player to a given position'''
        self._position = go_position

    def strategy(self) -> str:
        '''Returns a string with the name of the player's strategy'''
        return self._strategy

    def find_next_tile_of_type(self, board:Board, tile_type: str) -> Tile:
        tiles = board.tiles()
        num_tiles = len(tiles)
        for i in range(1, num_tiles + 1):
            next_index = (self.position() + i) % num_tiles
            tile = tiles[next_index]
            if tile.type() == tile_type:
                return tile
        
        return tiles[0]
    
    def add_get_out_of_jail_card(self) -> None:
        self._get_out_of_jail_free_cards += 1

    def put_in_prison(self) -> None:
        self._in_prison = True

    def release_from_prison(self) -> None:
        self._in_prison = False

    def is_in_prison(self) -> bool:
        return self._in_prison


def build_player(board: Board, data: dict[str, Any]) -> Player:
    """Build a Player from JSON-like dict with 'name', 'piece', and 'color' keys."""
    return Player(board, data["name"], data["piece"], data["color"], data["index"])
