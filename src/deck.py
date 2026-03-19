import json
import random
from card import Card, build_card


class Deck:

    _cards: list[Card]

    def __init__(self, path: str, deck_type:str) -> None:
        
        with open(path) as file:
            data = json.load(file)
        
        self._deck_type = deck_type
        self._cards = [build_card(card_data, self._deck_type) for card_data in data]

        self._discarded_cards: list[Card] = []

        self.shuffle()

    def shuffle(self) -> None:
        '''Shuffles the given deck'''
        random.shuffle(self._cards)

    def get_deck(self) -> list[Card]:
        '''Returns the given deck as a list of Card'''
        return self._cards
    
    def get_card(self) -> Card:
        '''Returns the last card of the given deck and handles what happens when a deck is empty'''
        if not self.get_deck():
            self._cards = self._discarded_cards
            self._discarded_cards = []
            self.shuffle()
        
        card = self.get_deck().pop()

        if card.action() != "get_out_of_jail_card":
            self._discarded_cards.append(card)

        return card
    
    def discard(self, card: Card) -> None:
        '''Returns a get out of jail card to the discarded pile'''
        self._discarded_cards.append(card)

    def get_discard_pile(self) -> list[Card]:
        return self._discarded_cards
