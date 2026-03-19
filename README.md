# Primera Pràctica d'AP2: Monopoly

## Índex
 
1. [Instruccions d'ús](#instruccions-dús)
2. [Arquitectura del projecte](#arquitectura-del-projecte)
3. [Especificació de mòduls, classes i mètodes](#especificació-de-mòduls-classes-i-mètodes)
4. [Decisions de disseny](#decisions-de-disseny)
5. [Joc de proves](#joc-de-proves)

## Instruccions d'ús
  
**Pas 1.** Executa el programa principal i introdueix el nombre de jugadors (entre 2 i 4):
 
```bash
python3 src/main.py
```
 
S'crearà automàticament una carpeta `output/` amb tots els fotogrames `.svg` de la partida.
 
**Pas 2.** Genera el fitxer HTML de visualització:
 
```bash
# macOS
python3 src/slideshow.py partida.html output/tauler-*.svg
 
# Windows (PowerShell)
python3 src/slideshow.py partida.html $(Get-ChildItem output/*.svg)
```
 
**Pas 3.** Obre `partida.html` des de l'explorador de fitxers al teu navegador.
 
---
## Arquitectura del projecte
 
```
src/
├── main.py           # Punt d'entrada
├── board.py          # Tauler i flux del joc
├── player.py         # Estat i accions dels jugadors
├── tile.py           # Caselles del tauler
├── card.py           # Cartes de Chance i Community Chest
├── deck.py           # Baralla de cartes
├── strategy.py       # Estratègies de decisió
├── draw.py           # Renderitzat SVG
├── const.py          # Constants globals
├── slideshow.py      # Generació del visualitzador HTML
├── data/
│   ├── tiles.json
│   ├── players.json
│   ├── chance.json
│   └── community-chest.json
└── tests/
    ├── test_tiles.py
    ├── test_cards.py
    ├── test_presó.py
    ├── test_bancarrota.py
    └── test_varied.py
```
---
## Arquitectura del projecte
El projecte està estructurat en diferents mòduls independents, però tots ells interconnectats per a facilitar el manteniment del codi i l'escalabilitat. Tot seguit mencionaré tots aquells mòduls que no estaven ja implementats al codi proporcionat.

### `board.py`
Conté la classe `Board`, que s'encarrega de gestionar el flux del joc, els torns i el tauler. En primer lloc, construeix tots els jugadors, cartes i caselles del joc a partir dels fitxers JSON. En segon lloc, conté tota una sèrie de mètodes per consultar informació de la partida: el jugador actual, les caselles, les baralles, l'estat dels daus, etc. Finalment, el mètode principal `play()` gestiona el bucle de joc: mentre quedi més d'un jugador viu, els jugadors que queden vius seguiran jugant. A continuació s'adjunten els diagrames de flux del mètode `play()`:
 
1a Part:
![Diagrama de flux de board.play(). Part 1](diagrama_1.png)
 
Continuació, 2a Part:
![Diagrama de flux de board.play(). Part 2](diagrama_2.png)
 
### `player.py`
Conté la classe `Player`, que s'encarrega de tot allò relacionat amb l'estat i les accions d'un jugador: el seu saldo, les seves propietats, la seva posició, l'estat de presó, les cartes de sortida de presó, el moviment pel tauler... Inclou també els mètodes `bankruptcy()` i `post_turn_actions()`, que gestionen respectivament la fallida del jugador i les decisions estratègiques que pren al final de cada tirada (construir cases, hipotecar, etc.).
 
### `tile.py`
Conté tota la lògica relacionada amb les caselles del tauler. Es basa en una jerarquia de classes: la classe base `Tile` i les subclasses `Tax`, `Card` i `Property` (que es subdivideix en `Street`, `Station` i `Utility`). Cada subclasse implementa el mètode `land_on()`, que defineix què passa quan un jugador cau en una casella d'aquella subclasse. A més a més, les caselles de tipus `Property` gestionen la compra, el lloguer, les hipoteques i la construcció de cases i hotels.
 
```
Tile
├── Property
│   ├── Street       (carrers amb cases i hotels)
│   ├── Station      (estacions de tren)
│   └── Utility      (empreses de serveis)
├── Tax              (caselles d'impostos)
└── Card             (caselles de Chance / Community Chest)
```
 
### `card.py`
Conté tota la lògica relacionada amb les cartes de Chance i Community Chest. Té una estructura similar a `tile.py`: la classe base `Card` i 11 subclasses, una per a cada acció possible (moure's a una posició, anar a la presó, cobrar diners, pagar per propietats, etc.). Cada subclasse té el mètode `execute()`, que s'encarrega d'executar l'acció corresponent a la carta.
 
### `deck.py`
Conté la classe `Deck`, que gestiona una baralla de cartes: la construeix a partir d'un fitxer JSON, la barreja, i en permet robar cartes. Quan la baralla es queda sense cartes torna a barrejar les cartes descartades. Les cartes de sortida de presó no es descarten fins que s'utilitzen, i si la carta era de Chance va a la baralla de descartades de Chance i igual per a Community Chest
 
### `strategy.py`
Conté les classes d'estratègia que determinen les decisions que pren cada jugador. La classe base `Strategy` defineix els mètodes `should_buy_property()`, `should_build_house()`, `should_sell_house()`, `should_mortgage_property()` i `should_unmortgage_property()`. Hi ha dues implementacions diferents, tal i com es menciona a l'apartat [Decisions de disseny](#decisions-de-disseny): `SimpleStrategy` i `AdvancedStrategy`.
 
### `const.py`
Defineix les constants globals del joc: el saldo inicial dels jugadors (`START_MONEY = 1500`), el salari de GO (`GO_SALARY = 50`), el nombre màxim de jugadors (`MAX_PLAYERS = 4`) i la llista de colors de grups de propietats (`COLORS`)
 
---

## Decisions de disseny
 
### Polimorfisme a `land_on` i `execute`
 En comptes d'implementar un llarguíssim mètode `land_on` ple d'ifs per a tots els tipus de caselles, vaig decidir fer ús del `polimorfisme` i implementar un mètode land_on a cada subclasse de la classe Tile. Igualment, cada subclasse de `Card` implementa el seu propi `execute`. Això permet afegir nous tipus de caselles o cartes sense modificar el codi existent, i fa que cada classe sigui responsable del seu propi comportament.
 
### Sistema de fallida simplificat
 El sistema de fallida ha esta una mica peculiar en aquest projecte, ja que estem limitats per unes normes més senzilles de les normals per tal de fer el projecte més senzill. Normalment, quan un jugador cau a una casella, pot realitzar totes les accions que vulgui, com hipotecar, vendre cases, negociar, etc., però en el nostre cas primer s'ha de complir amb les obligacions de la casella i després realitzar les accions post-torn. Per aquest motiu, en el monopoly, quan un jugador entra en fallida, primer intenta pagar el seu deute venent tot el que pot, i després, si continua sense poder pagar, li dona tot el seu patrimoni al jugador que li ha provocat la fallida. En el cas d'aquest projecte això no és possible, així que vaig decidir fer el següent:
 
- **Fallida envers el banc** (casella de tax, carta de pagament...): totes les cases s'eliminen, les propietats queden sense propietari i tornen al mercat lliures.
- **Fallida envers un altre jugador** (lloguer d'una propietat, carta de pagament a un altre jugador...): les propietats (amb les seves cases i estat hipotecat) es traspasssen íntegrament al creditor. Si aquest no pot pagar el 10% d'una hipoteca que rep, ell mateix pot entrar en fallida.
 
### Estratègia assignada per índex
 L'estratègia implementada és realment senzilla. Hi ha dues estratègies: SimpleStrategy i AdvancedStrategy, assignada a l'inici del joc la Simple als jugadors amb índex senar i la Advanced als jugadors amb índex parell. Els jugadors Advanced sempre mantenen unes reserves de diners (i per tant no compren si tot i tenir prou diners no són suficients per a mantenir-se per sobre de les reserves), i quan els seus diners baixen d'una certa quantitat, venen cases i propietats. En canvi, els jugadors Simple sempre que poden compren totes les propietats, no construeixen res, ni venen res.
 
### Salari de GO reduït
 Per tal de facilitar que la partida acabi en un número de partidews raonable, vaig decidir baixar el go_salary de 200$ a 50$, ja que si no la partida podia arribar a durar milers de torns. 
 
### Elecció del nombre de jugadors
 Com que no s'especificava de quina manera s'havia de poder escollir el nombre de jugadors de cada patida, vaig decidir que abans de començar es demanés, mitjançant un missatge a la terminal, el nombre de jugadors. En els tests, aquest input es simula automàticament.
 
### Go_To_Jail i dobles
 Si un jugador treu dobles i la carta de Chance o Community Chest l'envia a la presó, el torn s'acaba immediatament. Els dobles no li donen dret a una nova tirada.
 
### Generació d'SVG per fotograma
 Es genera un fitxer `.svg` diferent en els moments més significatius de la partida, intentant en tot moment que s'entengui què és el que està passant. Per exemple, si un jugador cau a una casella de Chance i aquesta l'obliga a anar a una altra casella, es crearan dos frames per a entendre millor el que ha passat. D'igual manera, quan un jugador entra en fallida, es crea un primer fram del jugador a la casella de la fallida sense haver realitzat la corresponent acció i després es mostra com el jugador s'elimina.

### Control dels sets de color
 Per tal de facilitar la cerca de carrers que formen part d'un color set complert, vaig decidir implementar un diccionari en què les claus són els colors dels diferents carrers i els valors són les propietats que es necessiten per a tenir el color set complert. De la mateixa manera, hi ha un altre diccionari per a cada jugador que indica quantes propietats de cada color set té.

---

## Joc de proves
 
Els tests es troben a `src/tests/` i s'executen amb `pytest`. Cada fitxer de test cobreix un àmbit específic:
 
| Fitxer | Àmbit |
|---|---|
| `test_tiles.py` | Compra de propietats, construcció i venda de cases i hotels, lloguers diferenciats, hipoteques |
| `test_cards.py` | Totes les accions de cartes de Chance i Community Chest, incloent casos de fallida |
| `test_presó.py` | Entrada a presó, sortida per dobles, per carta, per tres torns; tres dobles seguits... |
| `test_bancarrota.py` | Fallida envers el banc, envers un jugador, amb saldo zero i per culpa de carta |
 
### Estructura estàndard de cada test
 
1. **Creació de la carpeta `output/`**: es recrea per emmagatzemar els SVGs del test.
2. **Mock d'`input`**: s'evita demanar el nombre de jugadors per consola.
3. **Condicions inicials**: es fixa la posició, diners, propietats i cartes del jugador o jugadors que volem que participin en el test
4. **Mock dels daus**: `random.randint` es substitueix per un iterador amb valors predefinits per a que els jugadors es moguin a on volguem.
5. **Mock d'`alive_players`**: s'atura la partida després dels torns necessaris per al test.
6. **Execució i asserts**: es crida `tauler.play()` i es comprova l'estat final amb missatges d'error que indiquen si hi ha hagut algun error.