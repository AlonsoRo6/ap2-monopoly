from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from board import Board

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

    def description(self) -> str:
        return self._description
    
    def action(self) -> str:
        return self._action
    
    def execute(self, player:Player, board:Board) -> None:
        raise NotImplementedError


class Collect_Money(Card):

    def __init__(self, id:int, title:str, description:str, action:str, amount:int) -> None:
        super().__init__(id,title,description,action)
        self._amount = amount
    def get_amount(self) -> int:
        return self._amount
    
    def execute(self,player:Player, board:Board) -> None:
        player.add_money(self.get_amount())

class Move_To(Card):
    def __init__(self,id:int, title:str, description:str, action:str, position:int) -> None:
        super().__init__(id,title,description,action)
        self._position = position

    def get_position(self) -> int:
        return self._position
    
    def execute(self, player:Player, board:Board) -> None:
        player.move_to(self.get_position())
        tile = board.get_tile_index(self.get_position())
        tile.land_on(player,1,board)


class Move_To_Station(Card):
    def __init__(self, id: int, title: str, description: str, action: str, rent_multiplier: int) -> None:
        super().__init__(id, title, description, action)
        self._rent_multiplier = rent_multiplier

    def get_rent_multiplier(self) -> int:
        return self._rent_multiplier

    def execute(self,player:Player, board:Board) -> None:
        tile = player.find_next_tile_of_type(board,"station")
        player.move_to(tile.position())
        tile.land_on(player,self.get_rent_multiplier(),board)

class Move_To_Utility(Card):
    def __init__(self, id: int, title: str, description: str, action: str, rent_multiplier: int) -> None:
        super().__init__(id, title, description, action)
        self._rent_multiplier = rent_multiplier

    def get_rent_multiplier(self) -> int:
        return self._rent_multiplier

    def execute(self,player:Player, board:Board) -> None:
        tile = player.find_next_tile_of_type(board,"utility")
        player.move_to(tile.position())
        tile.land_on(player,self.get_rent_multiplier(),board)

class Get_Out_Of_Jail(Card):
    def __init__(self, id: int, title: str, description: str, action: str, keepCard: bool) -> None:
        super().__init__(id, title, description, action)

    def execute(self, player:Player, board:Board) -> None:
        player.add_get_out_of_jail_card()

class Move_Back(Card):
    def __init__(self, id: int, title: str, description: str, action: str, spaces:int) -> None:
        super().__init__(id, title, description, action)
        self._spaces = spaces
    
    def get_spaces(self) -> int:
        return self._spaces
    
    def execute(self, player:Player, board:Board) -> None:
        player.move_to(player.position()-self.get_spaces())
        tile = board.get_tile_index(player.position()-self.get_spaces())
        tile.land_on(player,1,board)

class Go_To_Jail(Card):
    def __init__(self, id: int, title: str, description: str, action: str) -> None:
        super().__init__(id, title, description, action)
    
    def execute(self, player:Player, board:Board) -> None:
        player.move_to(10)
        player.put_in_prison()

class Pay_Per_Property(Card):
    def __init__(self, id: int, title: str, description: str, action: str, amount_per_house:int, amount_per_hotel:int) -> None:
        super().__init__(id, title, description, action)
        self._amount_per_house = amount_per_house
        self._amount_per_hotel = amount_per_hotel
    def get_amount_per_house(self) -> int:
        return self._amount_per_house
    def get_amount_per_hotel(self) -> int:
        return self._amount_per_hotel
    
    def execute(self, player:Player, board:Board) -> None:
        from tile import Street
        for property in player.owned_properties():
            if isinstance(property,Street):
                houses = property.amount_houses()
                if 0 < houses < 5:
                    player.add_money(-houses * self.get_amount_per_house())
                elif houses == 5:
                    player.add_money(-self.get_amount_per_hotel())
                    
class Pay_Money(Card):
    def __init__(self, id: int, title: str, description: str, action: str, amount:int) -> None:
        super().__init__(id, title, description, action)
        self._amount = amount

    def get_amount(self) -> int:
        return self._amount
    
    def execute(self, player:Player, board:Board) -> None:
        player.add_money(-self.get_amount())
        
class Pay_Players(Card):
    def __init__(self, id: int, title: str, description: str, action: str, amount:int) -> None:
        super().__init__(id, title, description, action)    
        self._amount = amount

    def get_amount(self) -> int:
        return self._amount
    
    def execute(self,player:Player,board:Board) -> None:
        for oponent in board.players():
            if not oponent.is_bankrupt():
                oponent.add_money(self.get_amount())
                player.add_money(-self.get_amount())

class Collect_Players(Card):
    def __init__(self, id: int, title: str, description: str, action: str, amount:int) -> None:
        super().__init__(id, title, description, action)    
        self._amount = amount

    def get_amount(self) -> int:
        return self._amount
    
    def execute(self,player:Player,board:Board) -> None:
        for oponent in board.players():
            if not oponent.is_bankrupt():
                oponent.add_money(-self.get_amount())
                player.add_money(+self.get_amount())

def build_card(data: dict[str, Any]) -> Card: 
    card_action = data["action"]
    if card_action == "move_to_position":
        return Move_To(data["id"], data["title"], data["description"], data["action"], data["position"])
    
    elif card_action == "move_to_nearest_station":
        return Move_To_Station(data["id"], data["title"], data["description"], data["action"], data["rentMultiplier"])
    
    elif card_action == "move_to_nearest_utility":
        return Move_To_Utility(data["id"], data["title"], data["description"], data["action"], data["rentMultiplier"])
    
    elif card_action == "collect_money":
        return Collect_Money(data["id"], data["title"], data["description"], data["action"],data["amount"])
    
    elif card_action == "get_out_of_jail_card":
        return Get_Out_Of_Jail(data["id"], data["title"], data["description"], data["action"],data["keepCard"])
    
    elif card_action == "move_back_spaces":
        return Move_Back(data["id"], data["title"], data["description"], data["action"],data["spaces"])
    
    elif card_action == "go_to_jail":
        return Go_To_Jail(data["id"], data["title"], data["description"], data["action"])
    
    elif card_action == "pay_per_property":
        return Pay_Per_Property(data["id"], data["title"], data["description"], data["action"], data["amountPerHouse"], data["amountPerHotel"])
    
    elif card_action == "pay_money":
        return Pay_Money(data["id"], data["title"], data["description"], data["action"],data["amount"])
    
    elif card_action == "pay_each_player":
        return Pay_Players(data["id"], data["title"], data["description"], data["action"],data["amountPerPlayer"])
    
    elif card_action == "collect_from_players":
        return Collect_Players(data["id"], data["title"], data["description"], data["action"],data["amountPerPlayer"])
    
    else:
        return Card(data["id"], data["title"], data["description"], data["action"])


