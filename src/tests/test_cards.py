import random
import deck
from board import Board
from tile import *
from card import *
import const
import os
import shutil


def setup_test_scenario(posicio_inicial: int, input_val: str):
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
        players_json_path="src/data/players.json",
    )
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([2, 1])

    def mock_randint(a: int, b: int):
        return next(valors_daus)

    random.randint = mock_randint

    # Mock per aturar el bucle play()
    comptador = [0, 2]  # Llista per simular l'estat

    def mock_alive_players(self: Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1

    # Apliquem el mock al mètode de la instància
    tauler.alive_players = lambda: mock_alive_players(tauler)

    jugador = tauler.current_player()
    jugador.move_to(posicio_inicial)

    return tauler, jugador


def test_collect_money() -> None:
    """Test de les cartes d'acció collect_money"""
    tauler, jugador = setup_test_scenario(19, "2")

    # Forcem que la propera carta sigui anar a la presó
    carta = Collect_Money(
        50, "Bank Dividend", "Bank pays you dividend of £50", "collect_money", 50
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.money() == 1500 + carta.get_amount()
    ), "ERROR: La carta collect_money no ha donat els diners adequats"


def test_move_to() -> None:
    """Test de les cartes d'acció move_to_position"""
    tauler, jugador = setup_test_scenario(19, "2")

    # Forcem que la propera carta sigui anar a la presó
    carta = Move_To(
        1, "Advance to Go", "Advance to Go (Collect £200)", "move_to_position", 0
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.position() == 0
    ), "ERROR: El jugador no s'ha mogut a on hauria d'haver anat"
    assert (
        jugador.money() == 1500 + const.GO_SALARY
    ), "ERROR: No s'ha executat correctament l'acció de la casella"


def test_move_to_station() -> None:
    """Test de les cartes d'acció move_to_nearest_station"""
    tauler, jugador = setup_test_scenario(19, "2")

    rival = tauler.players()[1]

    propietat_rival = tauler.get_tile_index(25)
    assert isinstance(propietat_rival, Station)
    rival.new_property(propietat_rival)
    propietat_rival.set_owner(rival)

    # Forcem que la propera carta sigui anar a la presó
    carta = Move_To_Station(
        2,
        "Advance to Nearest Station (1)",
        "nearest Station. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental to which they are otherwise entitled",
        "move_to_nearest_station",
        2,
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.position() == 25
    ), "ERROR: El jugador no s'ha mogut a on hauria d'haver anat"
    assert (
        jugador.money() == 1500 - propietat_rival.get_rent() * 2
    ), "ERROR: No s'ha executat correctament l'acció de la casella"


def test_move_to_utility() -> None:
    """Test de les cartes d'acció move_to_nearest_station"""
    tauler, jugador = setup_test_scenario(19, "2")

    rival = tauler.players()[1]

    propietat_rival = tauler.get_tile_index(28)
    assert isinstance(propietat_rival, Utility)
    rival.new_property(propietat_rival)
    propietat_rival.set_owner(rival)

    # Forcem que la propera carta sigui anar a la presó
    carta = Move_To_Utility(
        2,
        "Advance to Nearest Utility",
        "Advance token to nearest Utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total ten times the amount thrown",
        "move_to_nearest_utility",
        10,
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.position() == 28
    ), "ERROR: El jugador no s'ha mogut a on hauria d'haver anat"
    assert (
        jugador.money() == 1500 - propietat_rival.get_rent() * 10
    ), "ERROR: No s'ha executat correctament l'acció de la casella"


def test_get_out_of_jail() -> None:
    """Test de les cartes d'acció get_out_of_jail"""
    tauler, jugador = setup_test_scenario(19, "2")

    # Forcem que la propera carta sigui anar a la presó
    carta = Get_Out_Of_Jail(
        0,
        "Get Out of Jail Free",
        "Get Out of Jail Free. This card may be kept until needed or sold",
        "get_out_of_jail_card",
        True,
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.get_out_of_jail_free_cards() == 1
    ), "ERROR: No s'ha afegit correctament la carta"
    assert (
        jugador.position() == 22
    ), "ERROR: No s'ha executat correctament l'acció de la casella"


def test_move_back() -> None:
    """Test de les cartes d'acció move_back_spaces"""
    tauler, jugador = setup_test_scenario(19, "2")

    rival = tauler.players()[1]
    prop_rival = tauler.get_tile_index(19)

    assert isinstance(prop_rival, Street)

    prop_rival.set_owner(rival)
    rival.new_property(prop_rival)

    # Forcem que la propera carta sigui anar a la presó
    carta = Move_Back(1, "Go Back 3 Spaces", "Go Back 3 Spaces", "move_back_spaces", 3)
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.position() == 19
    ), "ERROR: El jugador no s'ha mogut a on hauria d'haver anat"
    assert (
        jugador.money() == 1500 - prop_rival.get_rent()
    ), "ERROR: No s'ha executat correctament l'acció de la casella"


def test_go_to_jail() -> None:
    """Test de les cartes d'acció go_to_jail"""
    tauler, jugador = setup_test_scenario(19, "2")

    # Forcem que la propera carta sigui anar a la presó
    carta = Go_To_Jail(
        1,
        "Go to Jail",
        "Go to Jail. Go directly to Jail, do not pass Go, do not collect £200",
        "go_to_jail",
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.position() == 10
    ), "ERROR: El jugador no s'ha mogut a on hauria d'haver anat"
    assert (
        jugador.money() == 1500
    ), "ERROR: S'ha cobrat els diners de la casella de sortida"


def test_pay_per_property() -> None:
    """Test de les cartes d'acció pay_per_property quan té properties"""
    tauler, jugador = setup_test_scenario(19, "2")

    prop1 = tauler.get_tile_index(37)
    prop2 = tauler.get_tile_index(39)

    assert isinstance(prop1, Street) and isinstance(prop2, Street)
    prop1.set_owner(jugador)
    jugador.new_property(prop1)
    prop2.set_owner(jugador)
    jugador.new_property(prop2)

    for _ in range(4):
        prop1.buy_house()  # 4 cases
        prop2.buy_house()  # 4 cases

    prop1.buy_house()  # hotel

    # Forcem que la propera carta sigui anar a la presó
    carta = Pay_Per_Property(
        1,
        "General Repairs",
        "Make general repairs on all your property. For each house pay £25. For each hotel pay £100",
        "pay_per_property",
        25,
        100,
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.money() == 1500 - 4 * 25 - 100 - prop2.get_house_cost()
    ), "ERROR: No s'ha pagat el que tocava"  # com que té diners s'ha comprat un hotel


def test_pay_per_property_empty() -> None:
    """Test de les cartes d'acció pay_per_property quan no té properties"""
    tauler, jugador = setup_test_scenario(19, "2")

    # Forcem que la propera carta sigui anar a la presó
    carta = Pay_Per_Property(
        1,
        "General Repairs",
        "Make general repairs on all your property. For each house pay £25. For each hotel pay £100",
        "pay_per_property",
        25,
        100,
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert jugador.money() == 1500, "ERROR: No s'hauria d'haver pagat res"


def test_pay_money() -> None:
    """Test de les cartes d'acció pay_money"""
    tauler, jugador = setup_test_scenario(19, "2")

    # Forcem que la propera carta sigui anar a la presó
    carta = Pay_Money(0, "Speeding Fine", "Speeding fine £15", "pay_money", 50)
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.money() == 1500 - carta.get_amount()
    ), "ERROR: No ha pagat els diners adequats"


def test_pay_players() -> None:
    """Test de les cartes d'acció pay_each_player"""
    tauler, jugador = setup_test_scenario(19, "3")

    rival1 = tauler.players()[1]
    rival2 = tauler.players()[2]

    # Forcem que la propera carta sigui anar a la presó
    carta = Pay_Players(
        0,
        "Chairman of the Board",
        "You have been elected Chairman of the Board. Pay each player £50",
        "pay_each_player",
        50,
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert jugador.money() == 1500 - carta.get_amount() * (
        len(tauler.players()) - 1
    ), "ERROR: No s'ha pagat el que s'hauria d'haver pagat"
    assert (
        rival1.money() == 1500 + carta.get_amount()
    ), "ERROR: No s'ha pagat al jugador 1"
    assert (
        rival2.money() == 1500 + carta.get_amount()
    ), "ERROR: No s'ha pagat al jugador 2"


def test_pay_players_bakrupt():
    """Test de les cartes d'acció pay_each_player"""
    nom_carpeta = "output"
    if os.path.exists(nom_carpeta):
        shutil.rmtree(nom_carpeta)

    os.makedirs(nom_carpeta)
    path_gitignore = os.path.join(nom_carpeta, ".gitignore")
    with open(path_gitignore, "w") as f:
        f.write("*\n")

    import builtins

    builtins.input = lambda _: '3'

    # Setup del Board
    tauler = Board(
        tiles_json_path="src/data/tiles.json",
        chance_json_path="src/data/chance.json",
        community_chest_json_path="src/data/community-chest.json",
        players_json_path="src/data/players.json",
    )
    # Fem servir un iterador: cada vegada que cridem next(), ens dóna el següent número
    valors_daus = iter([2, 1])

    def mock_randint(a: int, b: int):
        return next(valors_daus)

    random.randint = mock_randint

    # Mock per aturar el bucle play()
    comptador = [0, 3, 3]  # Llista per simular l'estat

    def mock_alive_players(self: Board):
        if len(comptador) > 1:
            return comptador.pop()
        return 1

    # Apliquem el mock al mètode de la instància
    tauler.alive_players = lambda: mock_alive_players(tauler)

    jugador = tauler.current_player()
    jugador.move_to(19)
    jugador.add_money(-1425)
    rival1 = tauler.players()[1]
    rival2 = tauler.players()[2]

    # Forcem que la propera carta sigui anar a la presó
    carta = Pay_Players(
        0,
        "Chairman of the Board",
        "You have been elected Chairman of the Board. Pay each player £50",
        "pay_each_player",
        50,
    )
    deck.Deck.get_card = lambda self: carta
    tauler.play()

    assert jugador.is_bankrupt(), "ERROR: No s'ha pagat el que s'hauria d'haver pagat"
    assert rival1.money() == 1500, "ERROR: No s'hauria d'haver pagat al jugador 1"
    assert rival2.money() == 1500, "ERROR: No s'hauria d'haver pagat al jugador 2"

def test_collect_players() -> None:
    """Test de les cartes d'acció collect_each_player"""
    tauler, jugador = setup_test_scenario(14, "3")

    rival1 = tauler.players()[1]
    rival2 = tauler.players()[2]

    # Forcem que la propera carta sigui anar a la presó
    carta = Collect_Players(
        0,
        "CGrand Opera Night",
        "Grand Opera Night. Collect £50 from every player for opening night seats",
        "collect_from_players",
        50,
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert jugador.money() == 1500 + carta.get_amount() * (
        len(tauler.players()) - 1
    ), "ERROR: No s'ha rebut el que s'hauria d'haver rebut"
    assert (
        rival1.money() == 1500 - carta.get_amount()
    ), "ERROR: el jugador 1 no ha pagat"
    assert (
        rival2.money() == 1500 - carta.get_amount()
    ), "ERROR: El jugador 2 no ha pagat"


def test_collect_players_bakrupt():
    """Test de les cartes d'acció collect_each_player"""
    tauler, jugador = setup_test_scenario(14, "3")

    rival1 = tauler.players()[1]
    rival1.add_money(-1490)
    rival2 = tauler.players()[2]

    # Forcem que la propera carta sigui anar a la presó
    carta = Collect_Players(
        0,
        "CGrand Opera Night",
        "Grand Opera Night. Collect £50 from every player for opening night seats",
        "collect_from_players",
        50,
    )
    deck.Deck.get_card = lambda self: carta

    tauler.play()

    assert (
        jugador.money() == 1500 + carta.get_amount()
    ), "ERROR: No s'ha rebut el que s'hauria d'haver rebut"
    assert rival1.money() == 0, "ERROR: el jugador 1 no ha pagat"
    assert rival1.is_bankrupt(), "ERROR: el jugador 1 hauria d'estar en bancarrota"
    assert (
        rival2.money() == 1500 - carta.get_amount()
    ), "ERROR: El jugador 2 no ha pagat"
