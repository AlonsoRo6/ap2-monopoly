from __future__ import annotations
from board import Board
import random
import os
import shutil

def main() -> None:
    
    nom_carpeta = "output"
    if os.path.exists(nom_carpeta):
        shutil.rmtree(nom_carpeta)
    
    os.makedirs(nom_carpeta)
    path_gitignore = os.path.join(nom_carpeta, ".gitignore")
    with open(path_gitignore, "w") as f:
        f.write("*\n")


    board = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json",
    )
    
    random.seed()  
    board.play()


if __name__ == "__main__":
    main()
