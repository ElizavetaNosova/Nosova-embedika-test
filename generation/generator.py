from .init_tokenizer import init_kremlin_tokenizer
from .load_model import load_kremlin_gpt
from .utils import inflect_all
from .tags import BOS_TAG, PERSON_TAG, ORGANIZATION_TAG, TITLE_TAG
from .generation_parameters import get_generation_parameters
from .postprocessing import get_title_and_text

from typing import List, Tuple
from copy import copy


class KremlinGenerator():
    def __init__(self):
        self.gpt = load_kremlin_gpt().eval()
        self.tokenizer = init_kremlin_tokenizer()
        self._generation_parameters = get_generation_parameters(self.tokenizer)

    def generate(self,
                 person='',
                 organization='',
                 forse_person=False,
                 num_return_sequences=None) -> List[Tuple[str, str]]:
        prompt = self._format_prompt(person, organization, forse_person)
        encoding = self.tokenizer([prompt], return_tensors='pt').to(self.gpt.device)
        generation_parameters = copy(self._generation_parameters)
        if num_return_sequences is not None:
            generation_parameters['num_return_sequences'] = num_return_sequences
        gpt_output = self.gpt.generate(
            **encoding,
            **generation_parameters
        )
        decoded_output = [self.tokenizer.decode(i) for i in gpt_output.tolist()]
        return [get_title_and_text(i) for i in decoded_output]

    def _format_prompt(self,
                       person: str,
                       organization: str,
                       forse_person: bool):
        person = self._preprocess_person_entity(person)
        prompt = f'{BOS_TAG} {PERSON_TAG} {person} {ORGANIZATION_TAG} {organization} {TITLE_TAG}'
        # не делаю форсирование параметром по умолчанию
        # так как функция склонения меняет падеж всех слов, имеющих падеж,
        # а не только согласованных с вершиной именной группы. Может получиться аграмматичный текст,
        # но ожидается, что модель исправит его
        if forse_person:
            prompt = f'{prompt} {person}'
        return prompt

    def _preprocess_person_entity(self, person: str)->str:
        return inflect_all(person, 'datv')
