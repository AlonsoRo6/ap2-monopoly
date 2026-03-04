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
        players_json_path: str
    ): 

        with open(tiles_json_path, 'r', encoding='utf-8') as json_tiles:
            data_tiles = json.load(json_tiles)
        self._tiles = [build_tile(self,item) for item in data_tiles]
    
        self._chance = Deck(chance_json_path)
        self._community = Deck(community_chest_json_path)

        self._number_players = int(input('Number of players: ')) 
        assert 0 < self._number_players <= const.MAX_PLAYERS, '0 < number of players <= MAX_PLAYERS'

        with open(players_json_path, 'r', encoding='utf-8') as json_players:
            data_players = json.load(json_players)
        self._players = [build_player(self,item) for item in data_players]
        self._players = self._players[:self._number_players]
        
        self._current_player_index = 0
        self._dice1 = 0
        self._dice2 = 0

    def players(self) -> list[Player]: 
        '''Returns a list of Player with all players'''
        return self._players

    def tiles(self) -> list[Tile]: 
        '''Returns a list of Tile with all tiles'''
        return self._tiles

    def dice(self) -> tuple[int, int]:
        '''Returns the result of the last dice roll as a tuple'''
        return (self._dice1, self._dice2)

    def current_player(self) -> Player:
        '''Returns the current player as a Player'''
        return self._players[self._current_player_index]

    def num_tiles(self) -> int:
        '''Returns the number of tiles on the board'''
        return 40

    def jail_position(self) -> int:
        '''Returns the jail position on the board'''
        return 10

    
    def play(self,total_turns:int) -> None:
        '''Plays'''
        draw(self, "tauler-000.svg")
        numero_prova_taulell = 0
        
        for _ in range(total_turns):
            actual_player = self.current_player()
            
            self._dice1, self._dice2 = 0,0
            comptador_dobles = 0
            while self._dice1 == self._dice2: #Tirades dobles
                
                self._dice1, self._dice2 = random.randint(1,6), random.randint(1,6)
                
                if self._dice1 == self._dice2:
                    comptador_dobles += 1

                if comptador_dobles == 3:
                    print('gone to prison')
                    actual_player.move_to(self.jail_position())
                    
                    filename = f"tauler-{numero_prova_taulell + 1:03d}.svg"
                    draw(self, filename)
                    numero_prova_taulell += 1
                    break

                total_dice = self._dice1 + self._dice2
                print(f'{actual_player.name()} ha tret un {self._dice1} i un {self._dice2}')
                actual_player.move(total_dice)
                
                filename = f"tauler-{numero_prova_taulell + 1:03d}.svg"
                draw(self, filename)
                print()
                numero_prova_taulell += 1 #Nova tirada de daus -> nou taulell

            

            self._current_player_index += 1 #Passem al següent jugador
            if self._current_player_index == self._number_players:
                self._current_player_index = 0


    def get_tile_index(self, index: int) -> Tile:
        '''Method to get a tile given its index'''
        return self._tiles[index]
    


def save_board(board: Board, pickle_path: str) -> None:
    with open(pickle_path, "wb") as f:
        pickle.dump(board, f)


def load_board(pickle_path: str) -> Board:
    with open(pickle_path, "rb") as f:
        return pickle.load(f)
