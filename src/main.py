from __future__ import annotations
from board import Board
import random
#import player


def main() -> None:
    board = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json",
    )

    '''p1 = player.build_player(board, {"name": "Alonso", "piece": "Cotxe", "color": "Red"}, 0)  # jugador de proves
    p1.move(20)
    p1.move(25)'''
    random.seed(25)
    board.play(4)


if __name__ == "__main__":
    main()
