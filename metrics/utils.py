import re
from nltk.tokenize import wordpunct_tokenize


def get_tokens_without_punctuation(text):
    tokenized_text = wordpunct_tokenize(text)
    return [token for token in tokenized_text if re.search("[a-zA-Zа-яА-ЯёЁ\d]", token)]
