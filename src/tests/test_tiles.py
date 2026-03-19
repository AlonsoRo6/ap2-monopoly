import random
from board import Board
from tile import *
import const
import os
import shutil

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


def test_compra_una_propietat():
    tauler,jugador = setup_test_scenario(0,'2',[4,5])

    target_property = tauler.get_tile_index(9)
    assert isinstance(target_property,Street)
    
    tauler.play()

    assert len(jugador.owned_properties()) == 1, "ERROR: No s'ha comprat correctament les propietats"
    assert target_property.owner == tauler.players()[0], "ERROR, No s'ha assignat correctament el propietari"
    assert jugador.money() == (1500-120), "ERROR: No s'ha pagat la quantitat correcta"


def test_compra_cases():
    '''Donem al jugador ja dues propietats que completen un color, 
    i mirem si quan té la oportunitat compra o no una casa a cada carrer'''
    tauler,jugador = setup_test_scenario(0,'2',[6,4])

    propietat1 = tauler.get_tile_index(37)
    propietat2 = tauler.get_tile_index(39)

    assert isinstance(propietat1,Street)
    assert isinstance(propietat2,Street)

    jugador.new_property(propietat1)
    jugador.new_property(propietat2)
    propietat1.set_owner(jugador)
    propietat2.set_owner(jugador)
    
    tauler.play()

    assert propietat1.amount_houses() == 1, "ERROR: No s'ha comprat casa a propietat1"
    assert propietat2.amount_houses() == 1, "ERROR: No s'ha comprat casa a propietat2"
    assert jugador.money() == 1100, "ERROR: NO s'ha pagat el que s'hauria d'haver pagat"


def test_conversió_hotels():
    '''Comprova que la 5a casa es converteix en hotel'''
    tauler,jugador = setup_test_scenario(0,'2',[6,4])
    
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
    tauler,jugador = setup_test_scenario(39,'2',[1, 1, 3, 1])
    

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
    
    tauler.play()

    assert jugador.money() == 1500 + const.GO_SALARY - 4 - 50, "ERROR: No s'ha pagat el que tocava"
    # +50 per passar per la casella de sortida, 
    # -4 per lloguer del carrer de color del rival, 
    # -50 pel lloguer de tenir dues estacions de tren del rival


def test_mortgaged():
    '''Comprovem que si la casella està hipotecada no es paga res'''
    tauler,jugador = setup_test_scenario(0,'2',[5, 4])

    rival = tauler.players()[1]
    propietat_rival = tauler.get_tile_index(9)
    assert isinstance(propietat_rival,Street)
    rival.new_property(propietat_rival)
    propietat_rival.set_owner(rival)
    propietat_rival.mortgage()    
    
    tauler.play()

    assert jugador.money() == 1500, "ERROR: La Property està hipotecada però s'ha pagat rent igualment"


def test_can_mortgage():
    '''Comprovem que si el carrer té cases no es pot hipotecar'''
    tauler,jugador = setup_test_scenario(0,'2',[])

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

def test_mortgage():
    '''Comprovem que si el carrer té cases no es pot hipotecar'''
    tauler,jugador = setup_test_scenario(0,'2',[6,4])

    jugador.add_money(-1500)

    propietat1 = tauler.get_tile_index(37)
    propietat2 = tauler.get_tile_index(39)
    assert isinstance(propietat1,Street)
    assert isinstance(propietat2,Street)

    jugador.new_property(propietat1)
    jugador.new_property(propietat2)
    propietat1.set_owner(jugador)
    propietat2.set_owner(jugador) 

    tauler.play()
    assert jugador.owned_properties()[0].is_tile_mortgaged() == True, "ERROR: S'hauria d'haver hipotecat la propietat 1"
    assert jugador.owned_properties()[1].is_tile_mortgaged() == False, "ERROR: No s'hauria d'haver hipotecat la propietat 2"
    assert jugador.money() == propietat1.get_mortgage(), "ERROR: No ha rebut els diners adequats per hipotecar la propietat"


def test_can_sell_house():
    '''Comprovem que la venta uniforme de cases funciona correctament.1'''
    tauler,jugador = setup_test_scenario(0,'2',[])

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

    assert propietat2.can_sell_house() == True
    assert propietat1.can_sell_house() == False, "ERROR: No es pot vendre aquesta casa per la venda de cases uniforme"

def test_sell_house():
    '''Comprovem que la venta uniforme de cases funciona correctament.2'''
    tauler,jugador = setup_test_scenario(0,'2',[6,4])

    jugador.add_money(-1500)
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

    tauler.play()

    assert propietat2.can_sell_house() == True, "ERROR: S'hauria de poder vendre la casa"
    assert jugador.money() == propietat2.get_house_cost() // 2, "ERROR: No ha rebut els diners adequats"    

def test_unmortgage():
    '''Comprova que si té els diners necessaris, el jugador Advanced deshipoteca correctament la casella'''
    tauler,jugador = setup_test_scenario(0,'2',[6,4])

    propietat = tauler.get_tile_index(39)
    assert isinstance(propietat,Street)
    jugador.new_property(propietat)
    propietat.set_owner(jugador)
    propietat.mortgage()

    tauler.play()

    assert jugador.money() == 1500 - int(propietat.get_mortgage() * 1.1), "ERROR: No s'ha pagat el que s'hauria d'haver pagat per deshipotecar"
    assert not propietat.is_tile_mortgaged(), "ERROR: No s'ha deshipotecat la casella"


def test_transfer_mortgaged_property_both_bankrupt():
    '''Tenint una propietat hipotecada, cau en una propietat del rival i entra en fallida, 
    però el rival no pot pagar ni el 10% i també entra en fallida'''
    tauler,jugador = setup_test_scenario(38,'3',[2,1])

    propietat = tauler.get_tile_index(39)
    assert isinstance(propietat,Street)
    jugador.new_property(propietat)
    propietat.set_owner(jugador)
    propietat.mortgage()

    rival = tauler.players()[1]
    prop_rival = tauler.get_tile_index(1)
    assert isinstance(prop_rival,Street)
    prop_rival.set_owner(rival)
    rival.new_property(prop_rival)
    jugador.add_money(-1499)
    rival.add_money(-1499)
    tauler.play()

    assert jugador.is_bankrupt(), "ERROR: El jugador s'hauria d'haver arruinat"
    assert rival.is_bankrupt(), "ERROR: El rival s'hauria d'haver arruinat"

def test_transfer_mortgaged_property_and_unmortgage():
    '''Tenint una propietat hipotecada, cau en una propietat del rival i entra en fallida, 
    i el rival pot deshipotecar al moment'''
    tauler,jugador = setup_test_scenario(38,'3',[2,1])

    propietat = tauler.get_tile_index(39)
    assert isinstance(propietat,Street)
    jugador.new_property(propietat)
    propietat.set_owner(jugador)
    propietat.mortgage()

    rival = tauler.players()[1]
    prop_rival = tauler.get_tile_index(1)
    assert isinstance(prop_rival,Street)
    prop_rival.set_owner(rival)
    rival.new_property(prop_rival)
    jugador.add_money(-1499)
    tauler.play()

    assert jugador.is_bankrupt(), "ERROR: El jugador s'hauria d'haver arruinat"
    assert len(rival.owned_properties()) == 2, "ERROR: S'hauria d'haver traspassat la propietat"
    assert not propietat.is_tile_mortgaged(), "ERRRO: S'hauria d'haver deshipotecat"

def test_transfer_mortgaged_property_and_keep_unmortgaged():
    '''Tenint una propietat hipotecada, cau en una propietat del rival i entra en fallida, 
    i el rival no pot deshipotecar-la però sçi que pot pagar el 10%'''
    tauler,jugador = setup_test_scenario(38,'3',[2,1])

    propietat = tauler.get_tile_index(39)
    assert isinstance(propietat,Street)
    jugador.new_property(propietat)
    propietat.set_owner(jugador)
    propietat.mortgage()

    rival = tauler.players()[1]
    prop_rival = tauler.get_tile_index(1)
    assert isinstance(prop_rival,Street)
    prop_rival.set_owner(rival)
    rival.new_property(prop_rival)
    jugador.add_money(-1499)
    rival.add_money(-1450)
    tauler.play()

    assert jugador.is_bankrupt(), "ERROR: El jugador s'hauria d'haver arruinat"
    assert len(rival.owned_properties()) == 2, "ERROR: S'hauria d'haver traspassat la propietat"
    assert propietat.is_tile_mortgaged(), "ERRRO: No s'hauria d'haver deshipotecat, no té prou diners"