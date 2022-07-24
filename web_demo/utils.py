from typing import List
from nltk.tokenize import wordpunct_tokenize
from pymorphy2 import MorphAnalyzer

morph = MorphAnalyzer()

IGNORE_POS_TAGS = set(["NPRO", "PREP", "CONJ", "PRCL", "INTJ"])


def get_meaningful_tokens(*entities) -> List[str]:
    meaningful_tokens = []
    for entity in entities:
        entity_tokens = wordpunct_tokenize(entity)
        meaningful_tokens += [
            token
            for token in entity_tokens
            if len(token) > 1 and morph.parse(token)[0].tag.POS not in IGNORE_POS_TAGS
        ]
    return meaningful_tokens
