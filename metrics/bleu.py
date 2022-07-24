from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from statistics import mean
from typing import List

from metrics.utils import get_tokens_without_punctuation

smoothing_funtion = SmoothingFunction().method1


def bleu(generated_texts: List[str], gold_texts: List[str]):
    """
    Усредненная метрика sentence_bleu
    """
    tokenized_generated_texts = [
        get_tokens_without_punctuation(text) for text in generated_texts
    ]
    tokenized_gold_texts = [get_tokens_without_punctuation(text) for text in gold_texts]
    return mean(
        [
            sentence_bleu([gold], generated, smoothing_function=smoothing_funtion)
            for gold, generated in zip(tokenized_gold_texts, tokenized_generated_texts)
        ]
    )
