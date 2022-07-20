from nltk.tokenize import wordpunct_tokenize
from pymorphy2 import MorphAnalyzer, tagset

morph = MorphAnalyzer()

def inflect_token(token:str, case_tag:str)->str:
    if case_tag not in tagset.OpencorporaTag.CASES:
        raise ValueError('Unknown case tag')
    p = morph.parse(token)[0]
    # если у слова есть категория падежа, ставим в указанный падеж
    if len(token)>1 and p.tag.case:
        token_ = p.inflect({case_tag}).word
        #  pymorphy2 не сохраняет заглавные буквы при изменении формы слова
        if all([char.isupper() for char in token]):
            token_ = token.upper()
        elif token[0].isupper():
            token_ = token_.capitalize()
    else:
        token_ = token
    return token_

def inflect_all(entity:str, case_tag='datv')->str:
    tokens = wordpunct_tokenize(entity)
    return ' '.join([inflect_token(token, case_tag) for token in tokens])

