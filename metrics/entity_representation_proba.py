from nltk.stem.snowball import SnowballStemmer
from statistics import mean
from typing import List, Set
from functools import lru_cache

from .utils import get_tokens_without_punctuation

stemmer = SnowballStemmer("russian")


@lru_cache(maxsize=32)
def get_stem_set(text: str) -> Set[str]:
    tokens = get_tokens_without_punctuation(text)
    stems = [stemmer.stem(token) for token in tokens]
    return set(stems)


def entity_representation_proba(entities: List[str], text: str) -> float:
    if not entities:
        return None
    entities_stem_sets = [get_stem_set(entity) for entity in entities]
    text_stem_set = get_stem_set(text)

    are_presented = []
    for entity_idx, entity_stem_set in enumerate(entities_stem_sets):
        # дубли считаем только один раз
        if entity_stem_set not in entities_stem_sets[:entity_idx]:
            is_presented = all([stem in text_stem_set for stem in entity_stem_set])
            are_presented.append(is_presented)
    return mean(are_presented)


def corpus_entity_representation_proba(
    entities_groups: List[List[str]], texts: List[str]
):
    if len(entities_groups) != len(texts):
        raise ValueError()
    return mean(
        [
            entity_representation_proba(entities, text)
            for entities, text in zip(entities_groups, texts)
            if entities
        ]
    )
