from generation import KremlinGenerator
from metrics import entity_representation_proba
from .utils import get_meaningful_tokens

from typing import Tuple

generator = KremlinGenerator()

def generate(person, organization)->Tuple[str, str]:
    # при проверке будем рассматривать каждое слово самостоятельной части речи как отдельную сущность
    meaningful_tokens = get_meaningful_tokens(person, organization)
    # если нет токенов для проверки, мы не сможем ранжировать варианты
    # и достаточно сгенерировать один вариант поздравления
    if not meaningful_tokens:
        return generator.generate(person, organization, num_return_sequences=1)[0]

    versions = generator.generate(person, organization)
    version_scores = [entity_representation_proba(
        meaningful_tokens,
        ' '.join(version)
    ) for version in versions]
    max_score = max(version_scores)
    # если нужно было сгенерировать поздравление для персоны и модель с этим не справилась,
    # форсируем использование имени персоны в начале заголовка
    if person and not max_score:
        return generator.generate(person,
                                  organization,
                                  forse_person=True,
                                  num_return_sequences=1)[0]
    return versions[version_scores.index(max_score)]