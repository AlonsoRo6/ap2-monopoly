import json
import pickle
from player import Player
from tile import Tile, build_tile


class Board:

    def __init__(
        self,
        tiles_json_path: str,
        chance_json_path: str,
        community_chest_json_path: str,
        players_json_path: str,
    ): 
        self._tiles: list[Tile] = []
        with open(tiles_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            for item in data:
                new_tile = build_tile(self,item)
                self._tiles.append(new_tile)

    def players(self) -> list[Player]:
        return []

    def tiles(self) -> list[Tile]:
        return []

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
