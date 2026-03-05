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
        self._alive_players = 4

    def players(self) -> list[Player]: 
        '''Returns a list of Player with all players'''
        return self._players

    def alive_players(self) -> int:
        '''Returns the amount of still alive players'''
        return self._alive_players

    def eliminate_player(self) -> None:
        '''Eliminates a player from the player count'''
        self._alive_players -= 1


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

    
    def play(self) -> None:
        '''Plays'''
        draw(self, "output/tauler-000.svg")
        numero_prova_taulell = 0
        
        while self.alive_players() > 1:
            actual_player = self.current_player()
            
            if actual_player.is_bankrupt():
                self._current_player_index += 1 #Passem al següent jugador
                if self._current_player_index == self._number_players:
                    self._current_player_index = 0
                continue
            
            self._dice1, self._dice2 = 0,0
            comptador_dobles = 0
            while self._dice1 == self._dice2: #Tirades dobles
                
                self._dice1, self._dice2 = random.randint(1,6), random.randint(1,6)
                
                if self._dice1 == self._dice2:
                    comptador_dobles += 1

                if comptador_dobles == 3:
                    print('gone to prison')
                    actual_player.move_to(self.jail_position())
                    actual_player.put_in_prison()
                    
                    filename = f"output/tauler-{numero_prova_taulell + 1:03d}.svg"
                    draw(self, filename)
                    numero_prova_taulell += 1
                    break
                
                if actual_player.is_in_prison(): #dues maneres de sortir de la presó, i si no dibuixem i passem torn
                    print("A LA PRESÖ:",actual_player.name())
                    actual_player.add_turn_in_prison()

                    if comptador_dobles > 0:
                        actual_player.release_from_prison()
                    elif actual_player.get_out_of_jail_free_cards() > 0:
                        actual_player.release_from_prison()
                        actual_player.use_get_out_of_jail_card()
                    elif actual_player.turns_in_prison() == 3:
                        filename = f"output/tauler-{numero_prova_taulell + 1:03d}.svg"
                        draw(self, filename)
                        numero_prova_taulell += 1
                        actual_player.release_from_prison()
                        break
                    else:
                        filename = f"output/tauler-{numero_prova_taulell + 1:03d}.svg"
                        draw(self, filename)
                        numero_prova_taulell += 1
                        break
                        

                total_dice = self._dice1 + self._dice2 
                old_position = actual_player.position()
                print(f'{actual_player.name()} ha tret un {self._dice1} i un {self._dice2}')
                destination = (old_position + total_dice) % 40
                actual_player.move(total_dice,self)

                filename = f"output/tauler-{numero_prova_taulell + 1:03d}.svg"
                draw(self, filename)

                landed_tile = self.get_tile_index(actual_player.position())
                landed_tile.land_on(actual_player,1,self)
                actual_player.post_turn_actions()

                actual_position = self.get_tile_index(actual_player.position())
                if actual_player.money() < 0: #bankruptcy
                    
                    from tile import Property 
                    if isinstance(actual_position, Property):
                        actual_player.bankruptcy(actual_position.get_owner(),self)
                    else:
                        actual_player.bankruptcy(None,self)
                    
                    filename = f"output/tauler-{numero_prova_taulell + 1:03d}.svg"
                    draw(self, filename)
                    numero_prova_taulell += 1
                    self._dice1, self._dice2 = -1,0 #per si un cas la tirada en què cau en bancarrota havia tret dobles
                    break


                if actual_player.position() < old_position - 3 and not actual_player.is_in_prison() and not actual_player.is_bankrupt(): #casella de sortida
                    #old position - 3 per tenir en compte les cartes de Chance que fan anar 3 caselles enrere
                    actual_player.add_money(const.GO_SALARY)
                    print(f"You've gone through the GO tile and earned {const.GO_SALARY}$")
                    print(actual_player.money())

                if destination != actual_player.position():
                    numero_prova_taulell += 1 #hem caigut a chance o go to jail, així que tornem a dibuixar
                    filename = f"output/tauler-{numero_prova_taulell + 1:03d}.svg"
                    draw(self, filename)

                else: #no ens hem tornat a moure, actualitzem el dibuix que només tenia move per a mostrar els canvis en diners, propietats...
                    filename = f"output/tauler-{numero_prova_taulell + 1:03d}.svg"
                    draw(self, filename)
                
                numero_prova_taulell += 1 #Nova tirada de daus -> nou taulell
            

            self._current_player_index += 1 #Passem al següent jugador
            if self._current_player_index == self._number_players:
                self._current_player_index = 0
        
            print()


    def get_tile_index(self, index: int) -> Tile:
        '''Method to get a tile given its index'''
        return self._tiles[index]
    
    def get_deck(self, deck_type: str) -> Deck:
        '''Method to get a deck given the deck_type (chance or community)'''
        if deck_type == "chance":
            return self._chance
        return self._community


def save_board(board: Board, pickle_path: str) -> None:
    with open(pickle_path, "wb") as f:
        pickle.dump(board, f)


def load_board(pickle_path: str) -> Board:
    with open(pickle_path, "rb") as f:
        return pickle.load(f)
