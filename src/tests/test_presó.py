import random
import deck
from board import Board
from card import Go_To_Jail, Get_Out_Of_Jail
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


def test_simple_presó():
    '''Quan un jugador cau a la casella de la presó'''
    tauler,jugador = setup_test_scenario(27,'2',[2,1])

    tauler.play()

    posicio_final = jugador.position()
    assert posicio_final == 10, "ERROR: El jugador hauria d'estar a la posició de la presó'"
    
    esta_a_la_preso = jugador.is_in_prison()
    assert esta_a_la_preso == True, "ERROR: El jugador hauria d'estar marcat com a 'en presó'"

def test_dobles_presó():
    '''Comprova la següent situació: un jugador treu dobles, cau a una casella de chance que obliga a anar a la presó,
    i per tant, tot i tèncicament haver tret dobles a l'últim torn, no ha de sortir de la presó'''
    tauler,jugador = setup_test_scenario(14,'2',[4,4,1,2])

    # Forcem que la propera carta sigui anar a la presó
    carta_preso = Go_To_Jail(10, "Go to Jail", "Vés a la presó", "go_to_jail")
    deck.Deck.get_card = lambda self: carta_preso

    tauler.play()

    posicio_final = jugador.position()
    assert posicio_final == 10, "ERROR: El jugador hauria d'estar a la posició de la presó'"
    
    esta_a_la_preso = jugador.is_in_prison()
    assert esta_a_la_preso == True, "ERROR: El jugador hauria d'estar marcat com a 'en presó'"
    
def test_sortir_presó_dobles():
    '''Sortir de la presí amb daus dobles'''
    tauler,jugador = setup_test_scenario(10,'2',[4,4,1,2])
    
    jugador.put_in_prison()
    jugador.add_turn_in_prison()

    assert jugador.turns_in_prison() == 1, "ERROR, hauria de portar un torn a la presó"

    tauler.play()

    #posicio_final = jugador.position()
    assert not jugador.is_in_prison(), "ERROR: El jugador hauria d'estar fora de la presó'"
    assert jugador.position() == 21, "ERROR: El jguador hauria d'estar a la casella 21 (10+4+4+1+2)"
    
def test_sortir_presó_torns():
    '''Sortir de la presó per tres torns'''
    tauler,jugador = setup_test_scenario(10,'2',[3,2])
    
    jugador.put_in_prison()
    jugador.add_turn_in_prison()
    jugador.add_turn_in_prison()


    assert jugador.turns_in_prison() == 2, "ERROR, hauria de portar dos torns a la presó"
    tauler.play()

    #posicio_final = jugador.position()
    assert not jugador.is_in_prison(), "ERROR: El jugador hauria d'estar fora de la presó'"
    assert jugador.position() == 10, "ERROR: El jugador hauria d'estar a la casella 10"

def test_sortir_presó_carta():
    '''Sortir de la presó amb carta de sortir de la presó'''
    tauler,jugador = setup_test_scenario(10,'2',[3,2])
    
    jugador.put_in_prison()
    jugador.add_turn_in_prison()
    jugador.add_get_out_of_jail_card(Get_Out_Of_Jail(8, 'Get Out of Jail Free', 'Get Out of Jail Free. This card may be kept until needed or sold', 'get_out_of_jail_card', True, "chance"), tauler.get_deck("chance"))

    assert jugador.turns_in_prison() == 1, "ERROR, hauria de portar un torns a la presó"
    tauler.play()

    #posicio_final = jugador.position()
    assert not jugador.is_in_prison(), "ERROR: El jugador hauria d'estar fora de la presó'"
    assert jugador.position() == 15, "ERROR: El jugador hauria d'estar a la casella 10"
    
def test_tres_dobles():
    '''Quan un jugador treu tres dobles seguits'''
    tauler,jugador = setup_test_scenario(0,'2',[2,2,3,3,4,4])

    tauler.play()

    posicio_final = jugador.position()
    assert posicio_final == 10, "ERROR: El jugador hauria d'estar a la posició de la presó'"
    
    esta_a_la_preso = jugador.is_in_prison()
    assert esta_a_la_preso == True, "ERROR: El jugador hauria d'estar marcat com a 'en presó'"

def test_get_out_of_jail_card_returned_to_deck():
    '''Comprova que quan un jugador utilitza una carta de sortir de la presó,  aquesta es retorna correctament a la pila de descartades'''
    tauler, jugador = setup_test_scenario(10, '2', [3, 2])

    jugador.put_in_prison()
    jugador.add_turn_in_prison()
    
    carta = Get_Out_Of_Jail(8, 'Get Out of Jail Free', 'Get Out of Jail Free. This card may be kept until needed or sold', 'get_out_of_jail_card', True, "chance")
    deck_chance = tauler.get_deck("chance")
    jugador.add_get_out_of_jail_card(carta, deck_chance)

    cartes_abans = len(deck_chance.get_discard_pile())

    tauler.play()

    assert jugador.get_out_of_jail_free_cards() == 0, "ERROR: El jugador hauria d'haver utilitzat la carta"
    assert not jugador.is_in_prison(), "ERROR: El jugador hauria d'estar fora de la presó"
    assert len(deck_chance.get_discard_pile()) == cartes_abans + 1, "ERROR: La carta no s'ha retornat a la pila de descartades"
    assert deck_chance.get_discard_pile()[-1] is carta, "ERROR: La carta retornada no és la mateixa que s'havia donat"

    