import random
from board import Board
from tile import *
import os
import shutil
from card import *

def setup_test_scenario(posicio_inicial:int, input_val:str, dice_results:list[int]):
    nom_carpeta = "output"
    if os.path.exists(nom_carpeta):
        shutil.rmtree(nom_carpeta)
    
    os.makedirs(nom_carpeta)
    path_gitignore = os.path.join(nom_carpeta, ".gitignore")
    with open(path_gitignore, "w") as f:
        f.write("*\n")

    import builtins
    builtins.input = lambda _: input_val
    
    # Setup del Board
    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )
    
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter(dice_results) 
    def mock_randint(a:int, b:int):
        return next(valors_daus)

    random.randint = mock_randint
    
    # Mock per aturar el bucle play()
    comptador = [0, 2] # Llista per simular l'estat
    def mock_alive_players(self:Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1
    
    # Apliquem el mock al mètode de la instància
    tauler.alive_players = lambda: mock_alive_players(tauler)
    
    jugador = tauler.current_player()
    jugador.move_to(posicio_inicial)
    
    return tauler, jugador

def test_fallida_banca():
    '''Deixem al jugador només amb 150€, el portem a la casella de tax de 200€, 
    i previament li haviem assignat una Street amb una casa construida'''
    nom_carpeta = "output"
    if os.path.exists(nom_carpeta):
        shutil.rmtree(nom_carpeta)
    
    os.makedirs(nom_carpeta)
    path_gitignore = os.path.join(nom_carpeta, ".gitignore")
    with open(path_gitignore, "w") as f:
        f.write("*\n")

    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.current_player()
    jugador.add_money(-1400)
    propietat = tauler.get_tile_index(39)
    assert isinstance(propietat,Street)
    jugador.new_property(propietat)
    propietat.set_owner(jugador)
    propietat.buy_house()
    

    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([1, 3]) 
    
    def mock_randint(a:int, b:int):
        return next(valors_daus)

    random.randint = mock_randint    
    
    # Fem que el bucle de Board.play s'aturi després d'una iteració
    comptador = [0, 2] # Llista per simular l'estat
    def mock_alive_players(self:Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1
    
    tauler.alive_players = lambda: mock_alive_players(tauler)
    tauler.play()

    assert len(jugador.owned_properties()) == 0, "ERROR: No s'han eliminat correctament les propietats"
    
    assert propietat.amount_houses() == 0, "ERROR: S'haurien d'haver tret les cases"

def test_fallida_jugador():
    '''Deixem al jugador només amb 150€, el portem a la casella d'una estació propietat de l'altre jugador, amb una rent de 25€, 
    i previament li haviem assignat al jugador una Street amb una casa construida'''
    nom_carpeta = "output"
    if os.path.exists(nom_carpeta):
        shutil.rmtree(nom_carpeta)
    
    os.makedirs(nom_carpeta)
    path_gitignore = os.path.join(nom_carpeta, ".gitignore")
    with open(path_gitignore, "w") as f:
        f.write("*\n")
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]
    jugador.add_money(-1480) #el deixem amb 20 euros
    jugador.add_get_out_of_jail_card(Get_Out_Of_Jail(8, 'Get Out of Jail Free', 'Get Out of Jail Free. This card may be kept until needed or sold', 'get_out_of_jail_card', True, "chance"), tauler.get_deck("chance"))
    propietat = tauler.get_tile_index(39)
    assert isinstance(propietat,Street)
    jugador.new_property(propietat)
    propietat.set_owner(jugador)
    propietat.buy_house()


    rival = tauler.players()[1]
    propietat_rival = tauler.get_tile_index(5) #estació tren
    assert isinstance(propietat_rival,Station)
    rival.new_property(propietat_rival)
    propietat_rival.set_owner(rival)
    
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([2, 3]) 
    
    def mock_randint(a:int, b:int):
        return next(valors_daus)

    random.randint = mock_randint    
    
    # Fem que el bucle de Board.play s'aturi després d'una iteració
    comptador = [0, 2] # Llista per simular l'estat
    def mock_alive_players(self:Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1
    
    tauler.alive_players = lambda: mock_alive_players(tauler)
    tauler.play()

    assert len(jugador.owned_properties()) == 0, "ERROR: No s'han eliminat correctament les propietats"
    assert propietat.amount_houses() == 1, "ERROR: S'haurien d'haver tret les cases"
    assert propietat.get_owner() == rival, "ERROR: No s'ha traspassat correctament la propieta"
    assert rival.get_out_of_jail_free_cards() == 1, "ERROR: No s'ha traspassat la targeta de sortir de la presó"


def test_zero_money():
    """Portem al jugador de la casella 39 a la 1 i després a la 5. La casella 1 és propieta del rival, que també té la 3
    i per tant té el color set marró. La casella 5 també és del rival, que també té la 15 i per tant s'ha de pagar el doble
    a les estacions"""
    nom_carpeta = "output"
    if os.path.exists(nom_carpeta):
        shutil.rmtree(nom_carpeta)
    
    os.makedirs(nom_carpeta)
    path_gitignore = os.path.join(nom_carpeta, ".gitignore")
    with open(path_gitignore, "w") as f:
        f.write("*\n")
    
    import builtins
    builtins.input = lambda _: "2"  # per no haver de demanar l'input

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json",
    )

    jugador = tauler.players()[0]
    jugador.add_money(-1475)

    rival = tauler.players()[1]
    propietat_rival = tauler.get_tile_index(5)
    assert isinstance(propietat_rival,Station)
    rival.new_property(propietat_rival)
    propietat_rival.set_owner(rival)
    
    
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([2, 3])

    def mock_randint(a: int, b: int):
        return next(valors_daus)

    random.randint = mock_randint

    # Fem que el bucle de Board.play s'aturi després d'una iteració
    comptador = [0, 2]  # Llista per simular l'estat

    def mock_alive_players(self: Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1

    tauler.alive_players = lambda: mock_alive_players(tauler)
    tauler.play()

    assert jugador.money() == 0, "ERROR: No s'ha pagat el que tocava"
    assert jugador.is_bankrupt() == False, "ERROR: El jugador no hauria d'estar en bancarrota"