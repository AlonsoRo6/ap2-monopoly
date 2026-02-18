import json
import pickle
from player import Player, build_player
from tile import Tile, build_tile
from deck import Deck


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

    def players(self) -> list[Player]: ...

    def tiles(self) -> list[Tile]: return self._tiles

    def dice(self) -> tuple[int, int]:
        return (1, 1)

    def current_player(self) -> Player: ...

    def num_tiles(self) -> int:
        return 40

    def jail_position(self) -> int:
        return 10

    def play(self) -> None: ...


def save_board(board: Board, pickle_path: str) -> None:
    with open(pickle_path, "wb") as f:
        pickle.dump(board, f)


def load_board(pickle_path: str) -> Board:
    with open(pickle_path, "rb") as f:
        return pickle.load(f)
