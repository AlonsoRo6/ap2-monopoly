import random
from board import Board
from tile import *
import const

def test_compra_una_propietat():
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]
    target_property = tauler.get_tile_index(9)
    assert isinstance(target_property,Street)
    
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([4,5]) 
    
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

    assert len(jugador.owned_properties()) == 1, "ERROR: No s'ha comprat correctament les propietats"
    assert target_property.owner == tauler.players()[0], "ERROR, No s'ha assignat correctament el propietari"
    assert jugador.money() == (1500-120), "ERROR: No s'ha pagat la quantitat correcta"


def test_compra_cases():
    '''Donem al jugador ja dues propietats que completen un color, 
    i mirem si quan té la oportunitat compra o no una casa a cada carrer'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]
    propietat1 = tauler.get_tile_index(37)
    propietat2 = tauler.get_tile_index(39)

    assert isinstance(propietat1,Street)
    assert isinstance(propietat2,Street)

    jugador.new_property(propietat1)
    jugador.new_property(propietat2)
    propietat1.set_owner(jugador)
    propietat2.set_owner(jugador)
    
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([6, 4]) 
    
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

    assert propietat1.amount_houses() == 1, "ERROR: No s'ha comprat casa a propietat1"
    assert propietat2.amount_houses() == 1, "ERROR: No s'ha comprat casa a propietat2"
    assert jugador.money() == 1100, "ERROR: NO s'ha pagat el que s'hauria d'haver pagat"


def test_conversió_hotels():
    '''Comprova que la 5a casa es converteix en hotel'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]
    propietat1 = tauler.get_tile_index(37)
    propietat2 = tauler.get_tile_index(39)

    assert isinstance(propietat1,Street)
    assert isinstance(propietat2,Street)

    jugador.new_property(propietat1)
    jugador.new_property(propietat2)
    propietat1.set_owner(jugador)
    propietat2.set_owner(jugador)
    
    for _ in range(4):
        propietat1.buy_house()
        propietat2.buy_house()

    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([6, 4]) 
    
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

    assert propietat1.amount_houses() == 5, "ERROR: No s'ha comprat casa a propietat1"
    assert propietat2.amount_houses() == 5, "ERROR: No s'ha comprat casa a propietat2"
    assert propietat1.hotels == 1, "ERROR: No s'ha convertit la 5a casa a hotel a propietat2"
    assert propietat2.hotels == 1, "ERROR: No s'ha converitt la 5a casa a hotel a propietat2"
    assert jugador.money() == 1100, "ERROR: NO s'ha pagat el que s'hauria d'haver pagat"


def test_different_rents():
    '''Portem al jugador de la casella 39 a la 1 i després a la 5. La casella 1 és propietat del rival, que també té la 3
    i per tant té el color set marró. La casella 5 també és del rival, que també té la 15 i per tant s'ha de pagar el doble
    a les estacions'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]
    jugador.move_to(39)

    rival = tauler.players()[1]
    color1 = tauler.get_tile_index(1)
    color2 = tauler.get_tile_index(3)
    tren1 = tauler.get_tile_index(5)
    tren2 = tauler.get_tile_index(15)

    assert isinstance(color1,Street)
    assert isinstance(color2,Street)
    assert isinstance(tren1,Station)
    assert isinstance(tren2,Station)


    rival.new_property(color1)
    rival.new_property(color2)
    color1.set_owner(rival)
    color2.set_owner(rival)
    
    rival.new_property(tren1)
    rival.new_property(tren2)
    tren1.set_owner(rival)
    tren2.set_owner(rival)
    
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([1, 1, 3, 1]) 
    
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

    assert jugador.money() == 1500 + const.GO_SALARY - 4 - 50, "ERROR: No s'ha pagat el que tocava"
    # +50 per passar per la casella de sortida, 
    # -4 per lloguer del carrer de color del rival, 
    # -50 pel lloguer de tenir dues estacions de tren del rival


def test_mortgaged():
    '''Comprovem que si la casella està hipotecada no es paga res'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]

    rival = tauler.players()[1]
    propietat_rival = tauler.get_tile_index(9)
    assert isinstance(propietat_rival,Street)
    rival.new_property(propietat_rival)
    propietat_rival.set_owner(rival)
    propietat_rival.mortgage()    
    
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([5, 4]) 
    
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

    assert jugador.money() == 1500, "ERROR: La Property està hipotecada però s'ha pagat rent igualment"


def test_can_mortgage():
    '''Comprovem que si el carrer té cases no es pot hipotecar'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]

    propietat1 = tauler.get_tile_index(37)
    propietat2 = tauler.get_tile_index(39)
    assert isinstance(propietat1,Street)
    assert isinstance(propietat2,Street)

    jugador.new_property(propietat1)
    jugador.new_property(propietat2)
    propietat1.set_owner(jugador)
    propietat2.set_owner(jugador)

    propietat1.buy_house()
    propietat2.buy_house()    


    assert propietat1.can_mortgage() == False, "ERROR: La property té cases i per tant NO s'hauria de poder hipotecar"


def test_can_sell_house():
    '''Comprovem que la venta uniforme de cases funciona correctament'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]

    propietat1 = tauler.get_tile_index(37)
    propietat2 = tauler.get_tile_index(39)
    assert isinstance(propietat1,Street)
    assert isinstance(propietat2,Street)

    jugador.new_property(propietat1)
    jugador.new_property(propietat2)
    propietat1.set_owner(jugador)
    propietat2.set_owner(jugador)

    propietat1.buy_house()
    propietat2.buy_house() 
    propietat2.buy_house() 

    assert propietat1.can_sell_house() == False, "ERROR: No es pot vendre aquesta casa per la venda de cases uniforme"


def test_unmortgage():
    '''Comprova que si té els diners necessaris, el jugador Advanced deshipoteca correctament la casella'''
    import builtins
    builtins.input = lambda _: "2" #per no haver de demanar l'input 

    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json"
    )

    jugador = tauler.players()[0]

    propietat = tauler.get_tile_index(39)
    assert isinstance(propietat,Street)
    jugador.new_property(propietat)
    propietat.set_owner(jugador)
    propietat.mortgage()


    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([6, 4]) 
    
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

    assert jugador.money() == 1500 - int(propietat.get_mortgage() * 1.1), "ERROR: No s'ha pagat el que s'hauria d'haver pagat per deshipotecar"
    assert not propietat.is_tile_mortgaged(), "ERROR: No s'ha deshipotecat la casella"