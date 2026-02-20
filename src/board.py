from __future__ import annotations
from typing import TYPE_CHECKING

import json
import pickle
import random

if TYPE_CHECKING:
    from player import Player
    from tile import Tile

from deck import Deck
from tile import build_tile
from player import build_player
from draw import draw
import const


class Board:

    def __init__(
        self,
        tiles_json_path: str,
        chance_json_path: str,
        community_chest_json_path: str,
        players_json_path: str,
    ): 

        with open(tiles_json_path, 'r', encoding='utf-8') as json_tiles:
            data_tiles = json.load(json_tiles)
        self._tiles = [build_tile(self,item) for item in data_tiles]
    
        self._chance = Deck(chance_json_path)
        self._community = Deck(community_chest_json_path)

        with open(players_json_path, 'r', encoding='utf-8') as json_players:
            data_players = json.load(json_players)
        self._players = [build_player(self,item,0) for item in data_players]

    def players(self) -> list[Player]: 
        return self._players

    def tiles(self) -> list[Tile]: return self._tiles

    def dice(self) -> tuple[int, int]:
        return (1, 1)

    def current_player(self) -> Player:
        return self._players[0] 

    def num_tiles(self) -> int:
        return 40

    def jail_position(self) -> int:
        return 10

    def play(self,total_turns:int) -> None:
        num_players = const.MAX_PLAYERS
    
        for turn_count in range(total_turns):
            actual_player = self._players[turn_count%num_players]

            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            total_dice = dice1 + dice2
            print(f'Ha tret un {dice1} i un {dice2}')
            actual_player.move(total_dice)
            draw(self, "board.svg")
            input("Prem Enter per al següent torn...")

    def get_tile_index(self, index: int) -> Tile:
        '''Method to get a tile given its index'''
        return self._tiles[index]
    


def save_board(board: Board, pickle_path: str) -> None:
    with open(pickle_path, "wb") as f:
        pickle.dump(board, f)


def load_board(pickle_path: str) -> Board:
    with open(pickle_path, "rb") as f:
        return pickle.load(f)
