from __future__ import annotations
from heyq.nlp.parser import NLPEngine
from heyq.nlp.intent import Intents


def test_nlp_basic():
    nlp = NLPEngine()
    assert nlp.parse("Open flipkart").name == Intents.NAVIGATE
    assert nlp.parse("Search for iPhone 16 Pro").name == Intents.SEARCH
    assert nlp.parse("add to cart").name == Intents.ADD_TO_CART
    assert nlp.parse("checkout").name == Intents.CHECKOUT
