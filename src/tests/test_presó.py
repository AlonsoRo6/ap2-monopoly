import random
import deck
from board import Board
from card import Go_To_Jail


def test_simple_presó():
    '''Quan un jugador cau a la casella de la presó'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.current_player()
    jugador.move_to(27)
    
    valors_daus = iter([2,1])
    def mock_randint(a:int, b:int):
        return next(valors_daus)

    random.randint = mock_randint

    # Fem que el bucle de Board.play s'aturi després d'una iteració
    comptador = [0, 2] # Llista per simular l'estat
    def mock_alive_players(self:Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1

    # Apliquem el mock al mètode de la instància
    tauler.alive_players = lambda: mock_alive_players(tauler)

    tauler.play()

    posicio_final = jugador.position()
    assert posicio_final == 10, "ERROR: El jugador hauria d'estar a la posició de la presó'"
    
    esta_a_la_preso = jugador.is_in_prison()
    assert esta_a_la_preso == True, "ERROR: El jugador hauria d'estar marcat com a 'en presó'"

def test_dobles_presó():
    '''Comprova la següent situació: un jugador treu dobles, cau a una casella de chance que obliga a anar a la presó,
    i per tant, tot i tèncicament haver tret dobles a l'últim torn, no ha de sortir de la presó'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.current_player()
    jugador.move_to(14) 

    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([4, 4, 1, 2]) 
    
    def mock_randint(a:int, b:int):
        return next(valors_daus)

    random.randint = mock_randint

    # Forcem que la propera carta sigui anar a la presó
    carta_preso = Go_To_Jail(10, "Go to Jail", "Vés a la presó", "go_to_jail")
    deck.Deck.get_card = lambda self: carta_preso

    
    # Fem que el bucle de Board.play s'aturi després d'una iteració
    comptador = [0, 2] # Llista per simular l'estat
    def mock_alive_players(self:Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1
    
    # Apliquem el mock al mètode de la instància
    tauler.alive_players = lambda: mock_alive_players(tauler)
    

    tauler.play()

    posicio_final = jugador.position()
    assert posicio_final == 10, "ERROR: El jugador hauria d'estar a la posició de la presó'"
    
    esta_a_la_preso = jugador.is_in_prison()
    assert esta_a_la_preso == True, "ERROR: El jugador hauria d'estar marcat com a 'en presó'"
    
def test_sortir_presó_dobles():
    '''Sortir de la presí amb daus dobles'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.current_player()
    jugador.move_to(10)
    jugador.put_in_prison()
    jugador.add_turn_in_prison()

    assert jugador.turns_in_prison() == 1, "ERROR, hauria de portar un torn a la presó"
    

    valors_daus = iter([4, 4, 1, 2]) 
    
    def mock_randint(a:int, b:int):
        return next(valors_daus)

    random.randint = mock_randint

    # Fem que el bucle de Board.play s'aturi després d'una iteració
    comptador = [0, 2] # Llista per simular l'estat
    def mock_alive_players(self:Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1

    # Apliquem el mock al mètode de la instància
    tauler.alive_players = lambda: mock_alive_players(tauler)

    tauler.play()

    #posicio_final = jugador.position()
    assert not jugador.is_in_prison(), "ERROR: El jugador hauria d'estar fora de la presó'"
    assert jugador.position() == 21, "ERROR: El jguador hauria d'estar a la casella 21 (10+4+4+1+2)"
    
def test_sortir_presó_torns():
    '''Sortir de la presó amb daus dobles'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.current_player()
    jugador.move_to(10)
    jugador.put_in_prison()
    jugador.add_turn_in_prison()
    jugador.add_turn_in_prison()


    assert jugador.turns_in_prison() == 2, "ERROR, hauria de portar dos torns a la presó"
    

    valors_daus = iter([3, 2]) 
    
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

    #posicio_final = jugador.position()
    assert not jugador.is_in_prison(), "ERROR: El jugador hauria d'estar fora de la presó'"
    assert jugador.position() == 10, "ERROR: El jugador hauria d'estar a la casella 10"

def test_sortir_presó_carta():
    '''Sortir de la presó amb carta de sortir de la presó'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.current_player()
    jugador.move_to(10)
    jugador.put_in_prison()
    jugador.add_turn_in_prison()
    jugador.add_get_out_of_jail_card()

    assert jugador.turns_in_prison() == 1, "ERROR, hauria de portar un torns a la presó"
    

    valors_daus = iter([3, 2]) 
    
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

    #posicio_final = jugador.position()
    assert not jugador.is_in_prison(), "ERROR: El jugador hauria d'estar fora de la presó'"
    assert jugador.position() == 15, "ERROR: El jugador hauria d'estar a la casella 10"
    
def test_tres_dobles():
    '''Quan un jugador treu tres dobles seguits'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.current_player()
    
    valors_daus = iter([2,2,3,3,4,4])
    def mock_randint(a:int, b:int):
        return next(valors_daus)

    random.randint = mock_randint

    # Fem que el bucle de Board.play s'aturi després d'una iteració
    comptador = [0, 2] # Llista per simular l'estat
    def mock_alive_players(self:Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1

    # Apliquem el mock al mètode de la instància
    tauler.alive_players = lambda: mock_alive_players(tauler)

    tauler.play()

    posicio_final = jugador.position()
    assert posicio_final == 10, "ERROR: El jugador hauria d'estar a la posició de la presó'"
    
    esta_a_la_preso = jugador.is_in_prison()
    assert esta_a_la_preso == True, "ERROR: El jugador hauria d'estar marcat com a 'en presó'"

    